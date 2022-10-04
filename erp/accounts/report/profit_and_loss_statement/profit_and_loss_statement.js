// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


capkpi.require("assets/erp/js/financial_statements.js", function() {
	capkpi.query_reports["Profit and Loss Statement"] = $.extend({},
		erp.financial_statements);

	erp.utils.add_dimensions('Profit and Loss Statement', 10);

	capkpi.query_reports["Profit and Loss Statement"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return capkpi.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		}
	);
});
