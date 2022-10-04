// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.require("assets/erp/js/sales_trends_filters.js", function() {
	capkpi.query_reports["Sales Order Trends"] = {
		filters: erp.get_sales_trends_filters()
	}
});
