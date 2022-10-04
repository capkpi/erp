// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Service Level Agreement', {
	refresh: function(frm) {
		let allow_statuses = [];
		const exclude_statuses = ['Open', 'Closed', 'Resolved'];

		capkpi.model.with_doctype('Issue', () => {
			let statuses = capkpi.meta.get_docfield('Issue', 'status', frm.doc.name).options;
			statuses = statuses.split('\n');
			allow_statuses = statuses.filter((status) => !exclude_statuses.includes(status));
			frm.fields_dict.pause_sla_on.grid.update_docfield_property(
				'status', 'options', [''].concat(allow_statuses)
			);
		});
	}
});
