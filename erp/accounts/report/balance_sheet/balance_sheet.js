// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.require("assets/erp/js/financial_statements.js", function() {
	capkpi.query_reports["Balance Sheet"] = $.extend({}, erp.financial_statements);

	erp.utils.add_dimensions('Balance Sheet', 10);

	capkpi.query_reports["Balance Sheet"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	capkpi.query_reports["Balance Sheet"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check",
		"default": 1
	});
});
