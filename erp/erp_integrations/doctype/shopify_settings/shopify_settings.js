// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide("erp_integrations.shopify_settings");

capkpi.ui.form.on("Shopify Settings", "onload", function(frm){
	capkpi.call({
		method:"erp.erp_integrations.doctype.shopify_settings.shopify_settings.get_series",
		callback:function(r){
			$.each(r.message, function(key, value){
				set_field_options(key, value);
			});
		}
	});
	erp_integrations.shopify_settings.setup_queries(frm);
})

capkpi.ui.form.on("Shopify Settings", "app_type", function(frm) {
	frm.toggle_reqd("api_key", (frm.doc.app_type == "Private"));
	frm.toggle_reqd("password", (frm.doc.app_type == "Private"));
})

capkpi.ui.form.on("Shopify Settings", "refresh", function(frm){
	if(!frm.doc.__islocal && frm.doc.enable_shopify === 1){
		frm.toggle_reqd("price_list", true);
		frm.toggle_reqd("warehouse", true);
		frm.toggle_reqd("taxes", true);
		frm.toggle_reqd("company", true);
		frm.toggle_reqd("cost_center", true);
		frm.toggle_reqd("cash_bank_account", true);
		frm.toggle_reqd("sales_order_series", true);
		frm.toggle_reqd("customer_group", true);
		frm.toggle_reqd("shared_secret", true);

		frm.toggle_reqd("sales_invoice_series", frm.doc.sync_sales_invoice);
		frm.toggle_reqd("delivery_note_series", frm.doc.sync_delivery_note);

	}

	let app_link = "<a href='https://capkpicloud.com/marketplace/apps/ecommerce_integrations' target='_blank'>Ecommerce Integrations</a>"
	frm.dashboard.add_comment(__("Shopify Integration will be removed from ERP in Version 14. Please install {0} app to continue using it.", [app_link]), "yellow", true);

})

$.extend(erp_integrations.shopify_settings, {
	setup_queries: function(frm) {
		frm.fields_dict["warehouse"].get_query = function(doc) {
			return {
				filters:{
					"company": doc.company,
					"is_group": "No"
				}
			}
		}

		frm.fields_dict["taxes"].grid.get_field("tax_account").get_query = function(doc){
			return {
				"query": "erp.controllers.queries.tax_account_query",
				"filters": {
					"account_type": ["Tax", "Chargeable", "Expense Account"],
					"company": doc.company
				}
			}
		}

		frm.fields_dict["cash_bank_account"].get_query = function(doc) {
			return {
				filters: [
					["Account", "account_type", "in", ["Cash", "Bank"]],
					["Account", "root_type", "=", "Asset"],
					["Account", "is_group", "=",0],
					["Account", "company", "=", doc.company]
				]
			}
		}

		frm.fields_dict["cost_center"].get_query = function(doc) {
			return {
				filters:{
					"company": doc.company,
					"is_group": "No"
				}
			}
		}

		frm.fields_dict["price_list"].get_query = function() {
			return {
				filters:{
					"selling": 1
				}
			}
		}
	}
})
