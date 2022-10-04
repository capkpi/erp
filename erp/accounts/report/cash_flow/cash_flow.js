// Copyright (c) 2013, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erp/js/financial_statements.js", function() {
	frappe.query_reports["Cash Flow"] = $.extend({},
		erp.financial_statements);

	erp.utils.add_dimensions('Cash Flow', 10);

	// The last item in the array is the definition for Presentation Currency
	// filter. It won't be used in cash flow for now so we pop it. Please take
	// of this if you are working here.

	frappe.query_reports["Cash Flow"]["filters"].splice(8, 1);

	frappe.query_reports["Cash Flow"]["filters"].push(
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		}
	);
});
