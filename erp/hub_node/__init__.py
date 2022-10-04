# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


import capkpi


@capkpi.whitelist()
def enable_hub():
	hub_settings = capkpi.get_doc("Marketplace Settings")
	hub_settings.register()
	capkpi.db.commit()
	return hub_settings


@capkpi.whitelist()
def sync():
	hub_settings = capkpi.get_doc("Marketplace Settings")
	hub_settings.sync()
