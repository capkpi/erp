// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Shift Request', {
	setup: function(frm) {
		frm.set_query("approver", function() {
			return {
				query: "erp.hr.doctype.department_approver.department_approver.get_approvers",
				filters: {
					employee: frm.doc.employee,
					doctype: frm.doc.doctype
				}
			};
		});
		frm.set_query("employee", erp.queries.employee);
	},
});
