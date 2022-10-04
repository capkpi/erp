// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Loan Security Shortfall', {
	refresh: function(frm) {
		frm.add_custom_button(__("Add Loan Security"), function() {
			frm.trigger('shortfall_action');
		});
	},

	shortfall_action: function(frm) {
		capkpi.call({
			method: "erp.loan_management.doctype.loan_security_shortfall.loan_security_shortfall.add_security",
			args: {
				'loan': frm.doc.loan
			},
			callback: function(r) {
				if (r.message) {
					let doc = capkpi.model.sync(r.message)[0];
					capkpi.set_route("Form", doc.doctype, doc.name);
				}
			}
		});
	}
});
