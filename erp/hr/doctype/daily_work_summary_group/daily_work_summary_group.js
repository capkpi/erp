// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Daily Work Summary Group', {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Daily Work Summary'), function () {
				capkpi.set_route('List', 'Daily Work Summary');
			});
		}
	}
});
