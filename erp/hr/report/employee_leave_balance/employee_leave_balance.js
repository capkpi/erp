// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.query_reports["Employee Leave Balance"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": capkpi.defaults.get_default("year_start_date")
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": capkpi.defaults.get_default("year_end_date")
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": capkpi.defaults.get_user_default("Company")
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "employee_status",
			"label": __("Employee Status"),
			"fieldtype": "Select",
			"options": [
				"",
				{ "value": "Active", "label": __("Active") },
				{ "value": "Inactive", "label": __("Inactive") },
				{ "value": "Suspended", "label": __("Suspended") },
				{ "value": "Left", "label": __("Left") },
			],
			"default": "Active",
		}
	],

	onload: () => {
		capkpi.call({
			type: "GET",
			method: "erp.hr.utils.get_leave_period",
			args: {
				"from_date": capkpi.defaults.get_default("year_start_date"),
				"to_date": capkpi.defaults.get_default("year_end_date"),
				"company": capkpi.defaults.get_user_default("Company")
			},
			freeze: true,
			callback: (data) => {
				capkpi.query_report.set_filter_value("from_date", data.message[0].from_date);
				capkpi.query_report.set_filter_value("to_date", data.message[0].to_date);
			}
		});
	}
}
