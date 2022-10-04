// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Guardian', {
	refresh: function(frm) {
		if(!frm.doc.user && !frm.is_new()) {
			frm.add_custom_button(__("Invite as User"), function() {
				return capkpi.call({
					method: "erp.education.doctype.guardian.guardian.invite_guardian",
					args: {
						guardian: frm.doc.name
					},
					callback: function(r) {
						frm.set_value("user", r.message);
					}
				});
			});
		}
	}
});
