// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Loan Security Pledge', {
	calculate_amounts: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		capkpi.model.set_value(cdt, cdn, 'amount', row.qty * row.loan_security_price);
		capkpi.model.set_value(cdt, cdn, 'post_haircut_amount', cint(row.amount - (row.amount * row.haircut/100)));

		let amount = 0;
		let maximum_amount = 0;
		$.each(frm.doc.securities || [], function(i, item){
			amount += item.amount;
			maximum_amount += item.post_haircut_amount;
		});

		frm.set_value('total_security_value', amount);
		frm.set_value('maximum_loan_value', maximum_amount);
	}
});

capkpi.ui.form.on("Pledge", {
	loan_security: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (row.loan_security) {
			capkpi.call({
				method: "erp.loan_management.doctype.loan_security_price.loan_security_price.get_loan_security_price",
				args: {
					loan_security: row.loan_security
				},
				callback: function(r) {
					capkpi.model.set_value(cdt, cdn, 'loan_security_price', r.message);
					frm.events.calculate_amounts(frm, cdt, cdn);
				}
			});
		}
	},

	qty: function(frm, cdt, cdn) {
		frm.events.calculate_amounts(frm, cdt, cdn);
	},
});
