// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Volunteer', {
	refresh: function(frm) {

		capkpi.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Volunteer'};

		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			capkpi.contacts.render_address_and_contact(frm);
		} else {
			capkpi.contacts.clear_address_and_contact(frm);
		}
	}
});
