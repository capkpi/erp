// Copyright (c) 2016, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Eway Bill"] = {
	"filters": [
		{
			'fieldname': 'delivery_note',
			'label': __("Delivery Note"),
			'fieldtype': 'Link',
			'options': 'Delivery Note'
		},
		{
			'fieldname': 'posting_date',
			'label': __("Date"),
			'fieldtype': 'DateRange',
			'default': [capkpi.datetime.nowdate(), capkpi.datetime.nowdate()]
		},
		{
			'fieldname': 'customer',
			'label': __("Customer"),
			'fieldtype': 'Link',
			'options': 'Customer'
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": capkpi.defaults.get_user_default("Company")
		},
	]
}
