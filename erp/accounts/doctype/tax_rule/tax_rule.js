// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.ui.form.on("Tax Rule", "customer", function(frm) {
	if(frm.doc.customer) {
		capkpi.call({
			method:"erp.accounts.doctype.tax_rule.tax_rule.get_party_details",
			args: {
				"party": frm.doc.customer,
				"party_type": "customer"
			},
			callback: function(r) {
				if(!r.exc) {
					$.each(r.message, function(k, v) {
						frm.set_value(k, v);
					});
				}
			}
		});
	}
});

capkpi.ui.form.on("Tax Rule", "supplier", function(frm) {
	if(frm.doc.supplier) {
		capkpi.call({
			method:"erp.accounts.doctype.tax_rule.tax_rule.get_party_details",
			args: {
				"party": frm.doc.supplier,
				"party_type": "supplier"
			},
			callback: function(r) {
				if(!r.exc) {
					$.each(r.message, function(k, v) {
						frm.set_value(k, v);
					});
				}
			}
		});
	}
});
