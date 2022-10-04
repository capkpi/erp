// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Subcontracted Item To Be Received"] = {
	"filters": [
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
			reqd: 1
		},
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: capkpi.datetime.add_months(capkpi.datetime.month_start(), -1),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: capkpi.datetime.add_days(capkpi.datetime.month_start(),-1),
			reqd: 1
		},
	]
};
