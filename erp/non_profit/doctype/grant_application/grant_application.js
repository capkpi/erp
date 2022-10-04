// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Grant Application', {
	refresh: function(frm) {
		capkpi.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Grant Application'};

		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			capkpi.contacts.render_address_and_contact(frm);
		} else {
			capkpi.contacts.clear_address_and_contact(frm);
		}

		if(frm.doc.status == 'Received' && !frm.doc.email_notification_sent){
			frm.add_custom_button(__("Send Grant Review Email"), function() {
				capkpi.call({
					method: "erp.non_profit.doctype.grant_application.grant_application.send_grant_review_emails",
					args: {
						grant_application: frm.doc.name
					}
				});
			});
		}
	}
});
