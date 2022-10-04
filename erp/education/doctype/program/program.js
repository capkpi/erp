// Copyright (c) 2015, CapKPI Technologies and contributors
// For license information, please see license.txt

cur_frm.add_fetch('fee_structure', 'total_amount', 'amount');

frappe.ui.form.on("Program", "refresh", function(frm) {

});
