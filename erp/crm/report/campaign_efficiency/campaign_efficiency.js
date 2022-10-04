// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
capkpi.query_reports["Campaign Efficiency"] = {
	"filters": [
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
		}
	]
};
