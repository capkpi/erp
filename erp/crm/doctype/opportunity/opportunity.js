// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'erp/selling/sales_common.js' %}
capkpi.provide("erp.crm");

cur_frm.email_field = "contact_email";
capkpi.ui.form.on("Opportunity", {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Quotation': 'Quotation',
			'Supplier Quotation': 'Supplier Quotation'
		},

		frm.set_query("opportunity_from", function() {
			return{
				"filters": {
					"name": ["in", ["Customer", "Lead"]],
				}
			}
		});

		if (frm.doc.opportunity_from && frm.doc.party_name){
			frm.trigger('set_contact_link');
		}
	},
	contact_date: function(frm) {
		if(frm.doc.contact_date < capkpi.datetime.now_datetime()){
			frm.set_value("contact_date", "");
			capkpi.throw(__("Next follow up date should be greater than now."))
		}
	},

	onload_post_render: function(frm) {
		frm.get_field("items").grid.set_multiple_add("item_code", "qty");
	},

	party_name: function(frm) {
		frm.trigger('set_contact_link');

		if (frm.doc.opportunity_from == "Customer") {
			erp.utils.get_party_details(frm);
		} else if (frm.doc.opportunity_from == "Lead") {
			erp.utils.map_current_doc({
				method: "erp.crm.doctype.lead.lead.make_opportunity",
				source_name: frm.doc.party_name,
				frm: frm
			});
		}
	},

	onload_post_render: function(frm) {
		frm.get_field("items").grid.set_multiple_add("item_code", "qty");
	},

	status:function(frm){
		if (frm.doc.status == "Lost"){
			frm.trigger('set_as_lost_dialog');
		}

	},

	customer_address: function(frm, cdt, cdn) {
		erp.utils.get_address_display(frm, 'customer_address', 'address_display', false);
	},

	contact_person: erp.utils.get_contact_details,

	opportunity_from: function(frm) {
		frm.trigger('setup_opportunity_from');

		frm.set_value("party_name", "");
	},

	setup_opportunity_from: function(frm) {
		frm.trigger('setup_queries');
		frm.trigger("set_dynamic_field_label");
	},

	refresh: function(frm) {
		var doc = frm.doc;
		frm.trigger('setup_opportunity_from');
		erp.toggle_naming_series();

		if(!doc.__islocal && doc.status!=="Lost") {
			if(doc.with_items){
				frm.add_custom_button(__('Supplier Quotation'),
					function() {
						frm.trigger("make_supplier_quotation")
					}, __('Create'));

				frm.add_custom_button(__('Request For Quotation'),
					function() {
						frm.trigger("make_request_for_quotation")
					}, __('Create'));
			}

			if (frm.doc.opportunity_from != "Customer") {
				frm.add_custom_button(__('Customer'),
					function() {
						frm.trigger("make_customer")
					}, __('Create'));
			}

			frm.add_custom_button(__('Quotation'),
				function() {
					frm.trigger("create_quotation")
				}, __('Create'));
		}

		if(!frm.doc.__islocal && frm.perm[0].write && frm.doc.docstatus==0) {
			if(frm.doc.status==="Open") {
				frm.add_custom_button(__("Close"), function() {
					frm.set_value("status", "Closed");
					frm.save();
				});
			} else {
				frm.add_custom_button(__("Reopen"), function() {
					frm.set_value("lost_reasons",[])
					frm.set_value("status", "Open");
					frm.save();
				});
			}
		}
	},

	set_contact_link: function(frm) {
		if(frm.doc.opportunity_from == "Customer" && frm.doc.party_name) {
			capkpi.dynamic_link = {doc: frm.doc, fieldname: 'party_name', doctype: 'Customer'}
		} else if(frm.doc.opportunity_from == "Lead" && frm.doc.party_name) {
			capkpi.dynamic_link = {doc: frm.doc, fieldname: 'party_name', doctype: 'Lead'}
		}
	},

	set_dynamic_field_label: function(frm){
		if (frm.doc.opportunity_from) {
			frm.set_df_property("party_name", "label", frm.doc.opportunity_from);
		}
	},

	make_supplier_quotation: function(frm) {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.opportunity.opportunity.make_supplier_quotation",
			frm: frm
		})
	},

	make_request_for_quotation: function(frm) {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.opportunity.opportunity.make_request_for_quotation",
			frm: frm
		})
	},

})

// TODO commonify this code
erp.crm.Opportunity = capkpi.ui.form.Controller.extend({
	onload: function() {

		if(!this.frm.doc.status) {
			frm.set_value('status', 'Open');
		}
		if(!this.frm.doc.company && capkpi.defaults.get_user_default("Company")) {
			frm.set_value('company', capkpi.defaults.get_user_default("Company"));
		}
		if(!this.frm.doc.currency) {
			frm.set_value('currency', capkpi.defaults.get_user_default("Currency"));
		}

		this.setup_queries();
	},

	setup_queries: function() {
		var me = this;

		if(this.frm.fields_dict.contact_by.df.options.match(/^User/)) {
			this.frm.set_query("contact_by", erp.queries.user);
		}

		me.frm.set_query('customer_address', erp.queries.address_query);

		this.frm.set_query("item_code", "items", function() {
			return {
				query: "erp.controllers.queries.item_query",
				filters: {'is_sales_item': 1}
			};
		});

		me.frm.set_query('contact_person', erp.queries['contact_query'])

		if (me.frm.doc.opportunity_from == "Lead") {
			me.frm.set_query('party_name', erp.queries['lead']);
		}
		else if (me.frm.doc.opportunity_from == "Customer") {
			me.frm.set_query('party_name', erp.queries['customer']);
		}
	},

	create_quotation: function() {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.opportunity.opportunity.make_quotation",
			frm: cur_frm
		})
	},

	make_customer: function() {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.opportunity.opportunity.make_customer",
			frm: cur_frm
		})
	}
});

$.extend(cur_frm.cscript, new erp.crm.Opportunity({frm: cur_frm}));

cur_frm.cscript.item_code = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.item_code) {
		return capkpi.call({
			method: "erp.crm.doctype.opportunity.opportunity.get_item_details",
			args: {"item_code":d.item_code},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(k, v) {
						capkpi.model.set_value(cdt, cdn, k, v);
					});
					refresh_field('image_view', d.name, 'items');
				}
			}
		})
	}
}
