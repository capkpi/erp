// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide("erp");
cur_frm.email_field = "email_id";

erp.LeadController = capkpi.ui.form.Controller.extend({
	setup: function () {
		this.frm.make_methods = {
			'Customer': this.make_customer,
			'Quotation': this.make_quotation,
			'Opportunity': this.make_opportunity
		};

		this.frm.toggle_reqd("lead_name", !this.frm.doc.organization_lead);
	},

	onload: function () {
		this.frm.set_query("customer", function (doc, cdt, cdn) {
			return { query: "erp.controllers.queries.customer_query" }
		});

		this.frm.set_query("lead_owner", function (doc, cdt, cdn) {
			return { query: "capkpi.core.doctype.user.user.user_query" }
		});

		this.frm.set_query("contact_by", function (doc, cdt, cdn) {
			return { query: "capkpi.core.doctype.user.user.user_query" }
		});
	},

	refresh: function () {
		let doc = this.frm.doc;
		erp.toggle_naming_series();
		capkpi.dynamic_link = { doc: doc, fieldname: 'name', doctype: 'Lead' }

		if (!this.frm.is_new() && doc.__onload && !doc.__onload.is_customer) {
			this.frm.add_custom_button(__("Customer"), this.make_customer, __("Create"));
			this.frm.add_custom_button(__("Opportunity"), this.make_opportunity, __("Create"));
			this.frm.add_custom_button(__("Quotation"), this.make_quotation, __("Create"));
		}

		if (!this.frm.is_new()) {
			capkpi.contacts.render_address_and_contact(this.frm);
		} else {
			capkpi.contacts.clear_address_and_contact(this.frm);
		}
	},

	make_customer: function () {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.lead.lead.make_customer",
			frm: cur_frm
		})
	},

	make_opportunity: function () {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.lead.lead.make_opportunity",
			frm: cur_frm
		})
	},

	make_quotation: function () {
		capkpi.model.open_mapped_doc({
			method: "erp.crm.doctype.lead.lead.make_quotation",
			frm: cur_frm
		})
	},

	organization_lead: function () {
		this.frm.toggle_reqd("lead_name", !this.frm.doc.organization_lead);
		this.frm.toggle_reqd("company_name", this.frm.doc.organization_lead);
	},

	company_name: function () {
		if (this.frm.doc.organization_lead && !this.frm.doc.lead_name) {
			this.frm.set_value("lead_name", this.frm.doc.company_name);
		}
	},

	contact_date: function () {
		if (this.frm.doc.contact_date) {
			let d = moment(this.frm.doc.contact_date);
			d.add(1, "day");
			this.frm.set_value("ends_on", d.format(capkpi.defaultDatetimeFormat));
		}
	}
});

$.extend(cur_frm.cscript, new erp.LeadController({ frm: cur_frm }));
