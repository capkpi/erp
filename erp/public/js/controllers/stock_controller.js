// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide("erp.stock");

erp.stock.StockController = capkpi.ui.form.Controller.extend({
	onload: function() {
		// warehouse query if company
		if (this.frm.fields_dict.company) {
			this.setup_warehouse_query();
		}
	},

	setup_warehouse_query: function() {
		var me = this;
		erp.queries.setup_queries(this.frm, "Warehouse", function() {
			return erp.queries.warehouse(me.frm.doc);
		});
	},

	setup_posting_date_time_check: function() {
		// make posting date default and read only unless explictly checked
		capkpi.ui.form.on(this.frm.doctype, 'set_posting_date_and_time_read_only', function(frm) {
			if(frm.doc.docstatus == 0 && frm.doc.set_posting_time) {
				frm.set_df_property('posting_date', 'read_only', 0);
				frm.set_df_property('posting_time', 'read_only', 0);
			} else {
				frm.set_df_property('posting_date', 'read_only', 1);
				frm.set_df_property('posting_time', 'read_only', 1);
			}
		})

		capkpi.ui.form.on(this.frm.doctype, 'set_posting_time', function(frm) {
			frm.trigger('set_posting_date_and_time_read_only');
		});

		capkpi.ui.form.on(this.frm.doctype, 'refresh', function(frm) {
			// set default posting date / time
			if(frm.doc.docstatus==0) {
				if(!frm.doc.posting_date) {
					frm.set_value('posting_date', capkpi.datetime.nowdate());
				}
				if(!frm.doc.posting_time) {
					frm.set_value('posting_time', capkpi.datetime.now_time());
				}
				frm.trigger('set_posting_date_and_time_read_only');
			}
		});
	},

	show_stock_ledger: function() {
		var me = this;
		if(this.frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				capkpi.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				capkpi.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}

	},

	show_general_ledger: function() {
		var me = this;
		if(this.frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				capkpi.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				capkpi.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	}
});