// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Tax Withholding Category', {
	setup: function(frm) {
		frm.set_query("account", "accounts", function(doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			if (child.company) {
				return {
					filters: {
						'company': child.company
					}
				};
			}
		});
	}
});