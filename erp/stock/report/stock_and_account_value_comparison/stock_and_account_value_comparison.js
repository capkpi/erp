// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Stock and Account Value Comparison"] = {
	"filters": [
		{
			"label": __("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": capkpi.defaults.get_user_default("Company")
		},
		{
			"label": __("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			get_query: function() {
				var company = capkpi.query_report.get_filter_value('company');
				return {
					filters: {
						"account_type": "Stock",
						"company": company
					}
				}
			}
		},
		{
			"label": __("As On Date"),
			"fieldname": "as_on_date",
			"fieldtype": "Date",
			"default": capkpi.datetime.get_today(),
		},
	]
};
