// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.ui.form.on('Installation Note', {
	setup: function(frm) {
		capkpi.dynamic_link = {doc: frm.doc, fieldname: 'customer', doctype: 'Customer'}
		frm.set_query('customer_address', erp.queries.address_query);
		frm.set_query('contact_person', erp.queries.contact_query);
		frm.set_query('customer', erp.queries.customer);
	},
	onload: function(frm) {
		if(!frm.doc.status) {
			frm.set_value({ status:'Draft'});
		}
		if(frm.doc.__islocal) {
			frm.set_value({inst_date: capkpi.datetime.get_today()});
		}
	},
	customer: function(frm) {
		erp.utils.get_party_details(frm);
	},
	customer_address: function(frm) {
		erp.utils.get_address_display(frm);
	},
	contact_person: function(frm) {
		erp.utils.get_contact_details(frm);
	}
});

capkpi.provide("erp.selling");

// TODO commonify this code
erp.selling.InstallationNote = capkpi.ui.form.Controller.extend({
	refresh: function() {
		var me = this;
		if (this.frm.doc.docstatus===0) {
			this.frm.add_custom_button(__('From Delivery Note'),
				function() {
					erp.utils.map_current_doc({
						method: "erp.stock.doctype.delivery_note.delivery_note.make_installation_note",
						source_doctype: "Delivery Note",
						target: me.frm,
						date_field: "posting_date",
						setters: {
							customer: me.frm.doc.customer || undefined,
						},
						get_query_filters: {
							docstatus: 1,
							status: ["not in", ["Stopped", "Closed"]],
							per_installed: ["<", 99.99],
							company: me.frm.doc.company
						}
					})
				}, "fa fa-download", "btn-default"
			);
		}
	},
});

$.extend(cur_frm.cscript, new erp.selling.InstallationNote({frm: cur_frm}));
