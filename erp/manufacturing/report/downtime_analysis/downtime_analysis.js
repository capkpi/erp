// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Downtime Analysis"] = {
	"filters": [
		{
			label: __("From Date"),
			fieldname:"from_date",
			fieldtype: "Datetime",
			default: capkpi.datetime.convert_to_system_tz(capkpi.datetime.add_months(capkpi.datetime.now_datetime(), -1)),
			reqd: 1
		},
		{
			label: __("To Date"),
			fieldname:"to_date",
			fieldtype: "Datetime",
			default: capkpi.datetime.now_datetime(),
			reqd: 1,
		},
		{
			label: __("Machine"),
			fieldname: "workstation",
			fieldtype: "Link",
			options: "Workstation"
		}
	]
};
