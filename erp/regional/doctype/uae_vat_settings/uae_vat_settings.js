// Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('UAE VAT Settings', {
	onload: function(frm) {
		frm.set_query('account', 'uae_vat_accounts', function() {
			return {
				filters: {
					'company': frm.doc.company
				}
			};
		});
	}
});
