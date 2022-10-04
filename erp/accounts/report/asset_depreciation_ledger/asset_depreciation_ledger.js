// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.query_reports["Asset Depreciation Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": capkpi.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": capkpi.datetime.add_months(capkpi.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": capkpi.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"asset",
			"label": __("Asset"),
			"fieldtype": "Link",
			"options": "Asset"
		},
		{
			"fieldname":"finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book"
		},
		{
			"fieldname":"asset_category",
			"label": __("Asset Category"),
			"fieldtype": "Link",
			"options": "Asset Category"
		}
	]
}
