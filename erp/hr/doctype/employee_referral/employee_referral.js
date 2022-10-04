// Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on("Employee Referral", {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.status === "Pending") {
			frm.add_custom_button(__("Reject Employee Referral"), function() {
				capkpi.confirm(
					__("Are you sure you want to reject the Employee Referral?"),
					function() {
						frm.doc.status = "Rejected";
						frm.dirty();
						frm.save_or_update();
					},
					function() {
						window.close();
					}
				);
			});

			frm.add_custom_button(__("Create Job Applicant"), function() {
				frm.events.create_job_applicant(frm);
			}).addClass("btn-primary");
		}

		// To check whether Payment is done or not
		if (frm.doc.docstatus === 1 && frm.doc.status === "Accepted") {
			capkpi.db.get_list("Additional Salary", {
				filters: {
					ref_docname: cur_frm.doc.name,
					docstatus: 1
				},
				fields: ["count(name) as additional_salary_count"]
			}).then((data) => {

				let additional_salary_count = data[0].additional_salary_count;

				if (frm.doc.is_applicable_for_referral_bonus && !additional_salary_count) {
					frm.add_custom_button(__("Create Additional Salary"), function() {
						frm.events.create_additional_salary(frm);
					}).addClass("btn-primary");
				}
			});
		}



	},
	create_job_applicant: function(frm) {
		capkpi.model.open_mapped_doc({
			method: "erp.hr.doctype.employee_referral.employee_referral.create_job_applicant",
			frm: frm
		});
	},

	create_additional_salary: function(frm) {
		capkpi.call({
			method: "erp.hr.doctype.employee_referral.employee_referral.create_additional_salary",
			args: {
				doc: frm.doc
			},
			callback: function (r) {
				var doclist = capkpi.model.sync(r.message);
				capkpi.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	},
});
