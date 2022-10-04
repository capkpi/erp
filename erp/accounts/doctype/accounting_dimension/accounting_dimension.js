// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Accounting Dimension', {
	refresh: function(frm) {
		frm.set_query('document_type', () => {
			let invalid_doctypes = capkpi.model.core_doctypes_list;
			invalid_doctypes.push('Accounting Dimension', 'Project',
				'Cost Center', 'Accounting Dimension Detail', 'Company');

			return {
				filters: {
					name: ['not in', invalid_doctypes]
				}
			};
		});

		if (!frm.is_new()) {
			frm.add_custom_button(__('Show {0}', [frm.doc.document_type]), function () {
				capkpi.set_route("List", frm.doc.document_type);
			});

			let button = frm.doc.disabled ? "Enable" : "Disable";

			frm.add_custom_button(__(button), function() {

				frm.set_value('disabled', 1 - frm.doc.disabled);

				capkpi.call({
					method: "erp.accounts.doctype.accounting_dimension.accounting_dimension.disable_dimension",
					args: {
						doc: frm.doc
					},
					freeze: true,
					callback: function(r) {
						let message = frm.doc.disabled ? "Dimension Disabled" : "Dimension Enabled";
						frm.save();
						capkpi.show_alert({message:__(message), indicator:'green'});
					}
				});
			});
		}
	},

	document_type: function(frm) {

		frm.set_value('label', frm.doc.document_type);
		frm.set_value('fieldname', capkpi.model.scrub(frm.doc.document_type));

		capkpi.db.get_value('Accounting Dimension', {'document_type': frm.doc.document_type}, 'document_type', (r) => {
			if (r && r.document_type) {
				frm.set_df_property('document_type', 'description', "Document type is already set as dimension");
			}
		});
	},
});

capkpi.ui.form.on('Accounting Dimension Detail', {
	dimension_defaults_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.reference_document = frm.doc.document_type;
	}
});
