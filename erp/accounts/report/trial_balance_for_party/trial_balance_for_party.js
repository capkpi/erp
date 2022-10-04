// Copyright (c) 2013, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.query_reports["Trial Balance for Party"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": capkpi.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": capkpi.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				capkpi.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = capkpi.model.get_doc("Fiscal Year", fiscal_year);
					capkpi.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": capkpi.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": capkpi.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "Customer",
			"reqd": 1
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = capkpi.query_report.get_filter_value('party_type');
				var party = capkpi.query_report.get_filter_value('party');
				if(party && !party_type) {
					capkpi.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				var company = capkpi.query_report.get_filter_value('company');
				return {
					"doctype": "Account",
					"filters": {
						"company": company,
					}
				}
			}
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show zero values"),
			"fieldtype": "Check"
		}
	]
}
