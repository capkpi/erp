// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Lead Conversion Time"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			'reqd': 1,
			"default": capkpi.datetime.add_days(capkpi.datetime.nowdate(), -30)
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			'reqd': 1,
			"default":capkpi.datetime.nowdate()
		},
	]
};
