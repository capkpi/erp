// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Support Hour Distribution"] = {
	"filters": [
		{
			'lable': __("From Date"),
			'fieldname': 'from_date',
			'fieldtype': 'Date',
			'default': capkpi.datetime.nowdate(),
			'reqd': 1
		},
		{
			'lable': __("To Date"),
			'fieldname': 'to_date',
			'fieldtype': 'Date',
			'default': capkpi.datetime.nowdate(),
			'reqd': 1
		}
	]
}
