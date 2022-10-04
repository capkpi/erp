import capkpi
from capkpi.installer import remove_from_installed_apps


def execute():
	capkpi.reload_doc("erp_integrations", "doctype", "shopify_settings")
	capkpi.reload_doc("erp_integrations", "doctype", "shopify_tax_account")
	capkpi.reload_doc("erp_integrations", "doctype", "shopify_log")
	capkpi.reload_doc("erp_integrations", "doctype", "shopify_webhook_detail")

	if "erp_shopify" in capkpi.get_installed_apps():
		remove_from_installed_apps("erp_shopify")

		capkpi.delete_doc("Module Def", "erp_shopify")

		capkpi.db.commit()

		capkpi.db.sql("truncate `tabShopify Log`")

		setup_app_type()
	else:
		disable_shopify()


def setup_app_type():
	try:
		shopify_settings = capkpi.get_doc("Shopify Settings")
		shopify_settings.app_type = "Private"
		shopify_settings.update_price_in_erp_price_list = (
			0 if getattr(shopify_settings, "push_prices_to_shopify", None) else 1
		)
		shopify_settings.flags.ignore_mandatory = True
		shopify_settings.ignore_permissions = True
		shopify_settings.save()
	except Exception:
		capkpi.db.set_value("Shopify Settings", None, "enable_shopify", 0)
		capkpi.log_error(capkpi.get_traceback())


def disable_shopify():
	# due to capkpi.db.set_value wrongly written and enable_shopify being default 1
	# Shopify Settings isn't properly configured and leads to error
	shopify = capkpi.get_doc("Shopify Settings")

	if (
		shopify.app_type == "Public"
		or shopify.app_type == None
		or (shopify.enable_shopify and not (shopify.shopify_url or shopify.api_key))
	):
		capkpi.db.set_value("Shopify Settings", None, "enable_shopify", 0)
