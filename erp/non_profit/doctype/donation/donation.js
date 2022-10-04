// Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Donation', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1 && !frm.doc.paid) {
			frm.add_custom_button(__('Create Payment Entry'), function() {
				frm.events.make_payment_entry(frm);
			});
		}
	},

	make_payment_entry: function(frm) {
		return capkpi.call({
			method: 'erp.accounts.doctype.payment_entry.payment_entry.get_payment_entry',
			args: {
				'dt': frm.doc.doctype,
				'dn': frm.doc.name
			},
			callback: function(r) {
				var doc = capkpi.model.sync(r.message);
				capkpi.set_route('Form', doc[0].doctype, doc[0].name);
			}
		});
	},
});
