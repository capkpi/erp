// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.query_reports["Item-wise Purchase Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": capkpi.datetime.add_months(capkpi.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": capkpi.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": capkpi.defaults.get_user_default("Company")
		},
		{
			"fieldname":"mode_of_payment",
			"label": __("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment"
		},
		{
			"label": __("Group By"),
			"fieldname": "group_by",
			"fieldtype": "Select",
			"options": ["Supplier", "Item Group", "Item", "Invoice"]
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	}
}
