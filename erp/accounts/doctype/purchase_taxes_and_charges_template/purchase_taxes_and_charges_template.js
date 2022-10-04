// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.cscript.tax_table = "Purchase Taxes and Charges";

{% include "erp/public/js/controllers/accounts.js" %}

capkpi.ui.form.on("Purchase Taxes and Charges", "add_deduct_tax", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];

	if(!d.category && d.add_deduct_tax) {
		capkpi.msgprint(__("Please select Category first"));
		d.add_deduct_tax = '';
	}
	else if(d.category != 'Total' && d.add_deduct_tax == 'Deduct') {
		capkpi.msgprint(__("Cannot deduct when category is for 'Valuation' or 'Valuation and Total'"));
		d.add_deduct_tax = '';
	}
	refresh_field('add_deduct_tax', d.name, 'taxes');
});

capkpi.ui.form.on("Purchase Taxes and Charges", "category", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];

	if (d.category != 'Total' && d.add_deduct_tax == 'Deduct') {
		capkpi.msgprint(__("Cannot deduct when category is for 'Valuation' or 'Vaulation and Total'"));
		d.add_deduct_tax = '';
	}
	refresh_field('add_deduct_tax', d.name, 'taxes');
});
