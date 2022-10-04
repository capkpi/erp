# -*- coding: utf-8 -*-


import capkpi


def execute():
	"""
	Enable translatable in these fields
	- Customer Name
	- Supplier Name
	- Contact Name
	- Item Name/ Description
	- Address
	"""

	capkpi.reload_doc("core", "doctype", "docfield")
	capkpi.reload_doc("custom", "doctype", "custom_field")

	enable_for_fields = [
		["Customer", "customer_name"],
		["Supplier", "supplier_name"],
		["Contact", "first_name"],
		["Contact", "last_name"],
		["Item", "item_name"],
		["Item", "description"],
		["Address", "address_line1"],
		["Address", "address_line2"],
	]

	for f in enable_for_fields:
		capkpi.get_doc(
			{
				"doctype": "Property Setter",
				"doc_type": f[0],
				"doctype_or_field": "DocField",
				"field_name": f[1],
				"property": "translatable",
				"propery_type": "Check",
				"value": 1,
			}
		).db_insert()
