// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Restaurant', {
	refresh: function(frm) {
		frm.add_custom_button(__('Order Entry'), () => {
			capkpi.set_route('Form', 'Restaurant Order Entry');
		});
	}
});
