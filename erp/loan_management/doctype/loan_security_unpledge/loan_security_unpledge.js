// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Loan Security Unpledge', {
	refresh: function(frm) {

		if (frm.doc.docstatus == 1 && frm.doc.status == 'Approved') {
			frm.set_df_property('status', 'read_only', 1);
		}
	}
});
