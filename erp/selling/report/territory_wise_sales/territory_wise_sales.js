// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */


capkpi.query_reports["Territory-wise Sales"] = {
	"breadcrumb":"Selling",
	"filters": [
		{
			fieldname:"transaction_date",
			label: __("Transaction Date"),
			fieldtype: "DateRange",
			default: [capkpi.datetime.add_months(capkpi.datetime.get_today(),-1), capkpi.datetime.get_today()],
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		}
	]
};
