// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.provide("erp.accounts.dimensions");

capkpi.ui.form.on('Asset Value Adjustment', {
	setup: function(frm) {
		frm.add_fetch('company', 'cost_center', 'cost_center');
		frm.set_query('cost_center', function() {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				}
			}
		});
		frm.set_query('asset', function() {
			return {
				filters: {
					calculate_depreciation: 1,
					docstatus: 1
				}
			};
		});
	},

	onload: function(frm) {
		if(frm.is_new() && frm.doc.asset) {
			frm.trigger("set_current_asset_value");
		}

		erp.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},

	company: function(frm) {
		erp.accounts.dimensions.update_dimension(frm, frm.doctype);
	},

	asset: function(frm) {
		frm.trigger("set_current_asset_value");
	},

	finance_book: function(frm) {
		frm.trigger("set_current_asset_value");
	},

	set_current_asset_value: function(frm) {
		if (frm.doc.asset) {
			frm.call({
				method: "erp.assets.doctype.asset_value_adjustment.asset_value_adjustment.get_current_asset_value",
				args: {
					asset: frm.doc.asset,
					finance_book: frm.doc.finance_book
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('current_asset_value', r.message);
					}
				}
			});
		}
	}
});
