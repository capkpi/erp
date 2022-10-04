import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "pricing_rule")

	capkpi.db.sql(
		""" UPDATE `tabPricing Rule` SET price_or_product_discount = 'Price'
		WHERE ifnull(price_or_product_discount,'') = '' """
	)
