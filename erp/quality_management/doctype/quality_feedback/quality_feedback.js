// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Quality Feedback', {
	template: function(frm) {
		if (frm.doc.template) {
			frm.call('set_parameters');
		}
	}
});
