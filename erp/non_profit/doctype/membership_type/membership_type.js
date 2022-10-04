// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Membership Type', {
	refresh: function (frm) {
		capkpi.db.get_single_value('Non Profit Settings', 'enable_razorpay_for_memberships').then(val => {
			if (val) frm.set_df_property('razorpay_plan_id', 'hidden', false);
		});

		capkpi.db.get_single_value('Non Profit Settings', 'allow_invoicing').then(val => {
			if (val) frm.set_df_property('linked_item', 'hidden', false);
		});

		frm.set_query('linked_item', () => {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
	}
});
