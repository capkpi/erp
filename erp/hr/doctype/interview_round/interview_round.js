// Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on("Interview Round", {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Create Interview"), function() {
				frm.events.create_interview(frm);
			});
		}
	},
	create_interview: function(frm) {
		capkpi.call({
			method: "erp.hr.doctype.interview_round.interview_round.create_interview",
			args: {
				doc: frm.doc
			},
			callback: function (r) {
				var doclist = capkpi.model.sync(r.message);
				capkpi.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	}
});
