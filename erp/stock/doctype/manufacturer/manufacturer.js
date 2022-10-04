// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Manufacturer', {
	refresh: function(frm) {
		capkpi.dynamic_link = { doc: frm.doc, fieldname: 'name', doctype: 'Manufacturer' };
		if (frm.doc.__islocal) {
			hide_field(['address_html','contact_html']);
			capkpi.contacts.clear_address_and_contact(frm);
		}
		else {
			unhide_field(['address_html','contact_html']);
			capkpi.contacts.render_address_and_contact(frm);
		}
	}
});
