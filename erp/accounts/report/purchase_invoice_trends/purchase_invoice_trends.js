// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.require("assets/erp/js/purchase_trends_filters.js", function() {
	capkpi.query_reports["Purchase Invoice Trends"] = {
		filters: erp.get_purchase_trends_filters()
	}
});
