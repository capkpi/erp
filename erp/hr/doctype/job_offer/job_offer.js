// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide("erp.job_offer");

capkpi.ui.form.on("Job Offer", {
	onload: function (frm) {
		frm.set_query("select_terms", function() {
			return { filters: { hr: 1 } };
		});
	},

	setup: function (frm) {
		frm.email_field = "applicant_email";
	},

	select_terms: function (frm) {
		erp.utils.get_terms(frm.doc.select_terms, frm.doc, function (r) {
			if (!r.exc) {
				frm.set_value("terms", r.message);
			}
		});
	},

	refresh: function (frm) {
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted')
			&& (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
			frm.add_custom_button(__('Create Employee'),
				function () {
					erp.job_offer.make_employee(frm);
				}
			);
		}

		if(frm.doc.__onload && frm.doc.__onload.employee) {
			frm.add_custom_button(__('Show Employee'),
				function () {
					capkpi.set_route("Form", "Employee", frm.doc.__onload.employee);
				}
			);
		}
	}

});

erp.job_offer.make_employee = function (frm) {
	capkpi.model.open_mapped_doc({
		method: "erp.hr.doctype.job_offer.job_offer.make_employee",
		frm: frm
	});
};
