// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.ui.form.on("Email Digest", {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Now'), function() {
				capkpi.call({
					method: 'erp.setup.doctype.email_digest.email_digest.get_digest_msg',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						let d = new capkpi.ui.Dialog({
							title: __('Email Digest: {0}', [frm.doc.name]),
							width: 800
						});
						$(d.body).html(r.message);
						d.show();
					}
				});
			});

			frm.add_custom_button(__('Send Now'), function() {
				return frm.call('send', null, () => {
					capkpi.show_alert({ message: __("Message Sent"), indicator: 'green'});
				});
			});
		}
	}
});
