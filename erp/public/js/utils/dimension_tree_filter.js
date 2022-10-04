capkpi.provide('erp.accounts');

erp.accounts.dimensions = {
	setup_dimension_filters(frm, doctype) {
		this.accounting_dimensions = [];
		this.default_dimensions = {};
		this.fetch_custom_dimensions(frm, doctype);
	},

	fetch_custom_dimensions(frm, doctype) {
		let me = this;
		capkpi.call({
			method: "erp.accounts.doctype.accounting_dimension.accounting_dimension.get_dimensions",
			args: {
				'with_cost_center_and_project': true
			},
			callback: function(r) {
				me.accounting_dimensions = r.message[0];
				me.default_dimensions = r.message[1];
				me.setup_filters(frm, doctype);
			}
		});
	},

	setup_filters(frm, doctype) {
		if (this.accounting_dimensions) {
			this.accounting_dimensions.forEach((dimension) => {
				capkpi.model.with_doctype(dimension['document_type'], () => {
					let parent_fields = [];
					capkpi.meta.get_docfields(doctype).forEach((df) => {
						if (df.fieldtype === 'Link' && df.options === 'Account') {
							parent_fields.push(df.fieldname);
						} else if (df.fieldtype === 'Table') {
							this.setup_child_filters(frm, df.options, df.fieldname, dimension['fieldname']);
						}

						if (capkpi.meta.has_field(doctype, dimension['fieldname'])) {
							this.setup_account_filters(frm, dimension['fieldname'], parent_fields);
						}
					});
				});
			});
		}
	},

	setup_child_filters(frm, doctype, parentfield, dimension) {
		let fields = [];

		if (capkpi.meta.has_field(doctype, dimension)) {
			capkpi.model.with_doctype(doctype, () => {
				capkpi.meta.get_docfields(doctype).forEach((df) => {
					if (df.fieldtype === 'Link' && df.options === 'Account') {
						fields.push(df.fieldname);
					}
				});

				frm.set_query(dimension, parentfield, function(doc, cdt, cdn) {
					let row = locals[cdt][cdn];
					return erp.queries.get_filtered_dimensions(row, fields, dimension, doc.company);
				});
			});
		}
	},

	setup_account_filters(frm, dimension, fields) {
		frm.set_query(dimension, function(doc) {
			return erp.queries.get_filtered_dimensions(doc, fields, dimension, doc.company);
		});
	},

	update_dimension(frm, doctype) {
		if (this.accounting_dimensions) {
			this.accounting_dimensions.forEach((dimension) => {
				if (frm.is_new()) {
					if (frm.doc.company && Object.keys(this.default_dimensions || {}).length > 0
						&& this.default_dimensions[frm.doc.company]) {

						let default_dimension = this.default_dimensions[frm.doc.company][dimension['fieldname']];

						if (default_dimension) {
							if (capkpi.meta.has_field(doctype, dimension['fieldname'])) {
								frm.set_value(dimension['fieldname'], default_dimension);
							}

							$.each(frm.doc.items || frm.doc.accounts || [], function(i, row) {
								capkpi.model.set_value(row.doctype, row.name, dimension['fieldname'], default_dimension);
							});
						}
					}
				}
			});
		}
	},

	copy_dimension_from_first_row(frm, cdt, cdn, fieldname) {
		if (capkpi.meta.has_field(frm.doctype, fieldname) && this.accounting_dimensions) {
			this.accounting_dimensions.forEach((dimension) => {
				let row = capkpi.get_doc(cdt, cdn);
				frm.script_manager.copy_from_first_row(fieldname, row, [dimension['fieldname']]);
			});
		}
	}
};
