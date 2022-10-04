import capkpi


def execute():
	capkpi.reload_doc("erp_integrations", "doctype", "shopify_settings")
	capkpi.db.set_value("Shopify Settings", None, "app_type", "Private")
