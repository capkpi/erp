# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import capkpi

from erp.erp_integrations.doctype.shopify_settings.shopify_settings import (
	setup_custom_fields,
)


def execute():
	if capkpi.db.get_single_value("Shopify Settings", "enable_shopify"):
		setup_custom_fields()
