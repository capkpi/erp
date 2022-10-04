// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Process Loan Security Shortfall', {
	onload: function(frm) {
		frm.set_value('update_time', capkpi.datetime.now_datetime());
	}
});
