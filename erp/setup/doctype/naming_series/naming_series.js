// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


capkpi.ui.form.on("Naming Series", {
	onload: function(frm) {
		frm.events.get_doc_and_prefix(frm);
	},

	refresh: function(frm) {
		frm.disable_save();
	},

	get_doc_and_prefix: function(frm) {
		capkpi.call({
			method: "get_transactions",
			doc: frm.doc,
			callback: function(r) {
				frm.set_df_property("select_doc_for_series", "options", r.message.transactions);
				frm.set_df_property("prefix", "options", r.message.prefixes);
			}
		});
	},

	select_doc_for_series: function(frm) {
		frm.set_value("user_must_always_select", 0);
		capkpi.call({
			method: "get_options",
			doc: frm.doc,
			callback: function(r) {
				frm.set_value("set_options", r.message);
				if(r.message && r.message.split('\n')[0]=='')
					frm.set_value('user_must_always_select', 1);
				frm.refresh();
			}
		});
	},

	prefix: function(frm) {
		capkpi.call({
			method: "get_current",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_field("current_value");
			}
		});
	},

	update: function(frm) {
		capkpi.call({
			method: "update_series",
			doc: frm.doc,
			callback: function(r) {
				frm.events.get_doc_and_prefix(frm);
			}
		});
	},

	naming_series_to_check(frm) {
		capkpi.call({
			method: "preview_series",
			doc: frm.doc,
			callback: function(r) {
				if (!r.exc) {
					frm.set_value("preview", r.message);
				} else {
					frm.set_value("preview", __("Failed to generate preview of series"));
				}
			}
		});
	},

	add_series(frm) {
		const series = frm.doc.naming_series_to_check;

		if (!series) {
			capkpi.show_alert(__("Please type a valid series."));
			return;
		}

		if (!frm.doc.set_options.includes(series)) {
			const current_series = frm.doc.set_options;
			frm.set_value("set_options", `${current_series}\n${series}`);
		} else {
			capkpi.show_alert(__("Series already added to transaction."));
		}
	},
});
