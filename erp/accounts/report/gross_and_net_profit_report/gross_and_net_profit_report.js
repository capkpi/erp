// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.query_reports["Gross and Net Profit Report"] = {
	"filters": [

	]
}
capkpi.require("assets/erp/js/financial_statements.js", function() {
	capkpi.query_reports["Gross and Net Profit Report"] = $.extend({},
		erp.financial_statements);

	capkpi.query_reports["Gross and Net Profit Report"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return capkpi.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		}
	);
});
