// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('DATEV Settings', {
	refresh: function(frm) {
		frm.add_custom_button('Show Report', () => capkpi.set_route('query-report', 'DATEV'), "fa fa-table");
	}
});
