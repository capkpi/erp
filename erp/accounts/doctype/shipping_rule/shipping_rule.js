// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide('erp.accounts.dimensions');

capkpi.ui.form.on('Shipping Rule', {
	onload: function(frm) {
		erp.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},

	company: function(frm) {
		erp.accounts.dimensions.update_dimension(frm, frm.doctype);
	},

	refresh: function(frm) {
		frm.set_query("account", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})

		frm.trigger('toggle_reqd');
	},
	calculate_based_on: function(frm) {
		frm.trigger('toggle_reqd');
	},
	toggle_reqd: function(frm) {
		frm.toggle_reqd("shipping_amount", frm.doc.calculate_based_on === 'Fixed');
		frm.toggle_reqd("conditions", frm.doc.calculate_based_on !== 'Fixed');
	}
});
