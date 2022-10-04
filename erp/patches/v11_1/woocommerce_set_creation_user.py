import capkpi
from capkpi.utils import cint


def execute():
	capkpi.reload_doc("erp_integrations", "doctype", "woocommerce_settings")
	doc = capkpi.get_doc("Woocommerce Settings")

	if cint(doc.enable_sync):
		doc.creation_user = doc.modified_by
		doc.save(ignore_permissions=True)
