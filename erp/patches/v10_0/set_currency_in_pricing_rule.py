import capkpi


def execute():
	capkpi.reload_doctype("Pricing Rule")

	currency = capkpi.db.get_default("currency")
	for doc in capkpi.get_all("Pricing Rule", fields=["company", "name"]):
		if doc.company:
			currency = capkpi.get_cached_value("Company", doc.company, "default_currency")

		capkpi.db.sql(
			"""update `tabPricing Rule` set currency = %s where name = %s""", (currency, doc.name)
		)
