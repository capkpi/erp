// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


capkpi.query_reports["Absent Student Report"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": capkpi.datetime.get_today(),
			"reqd": 1
		}
	]
}
