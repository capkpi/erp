import capkpi


def execute():
	capkpi.reload_doc("hub_node", "doctype", "Marketplace Settings")
	capkpi.db.set_value(
		"Marketplace Settings", "Marketplace Settings", "marketplace_url", "https://hubmarket.org"
	)
