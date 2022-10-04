# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("stock", "doctype", "item_barcode")
	if capkpi.get_all("Item Barcode", limit=1):
		return
	if "barcode" not in capkpi.db.get_table_columns("Item"):
		return

	items_barcode = capkpi.db.sql(
		"select name, barcode from tabItem where barcode is not null", as_dict=True
	)
	capkpi.reload_doc("stock", "doctype", "item")

	for item in items_barcode:
		barcode = item.barcode.strip()

		if barcode and "<" not in barcode:
			try:
				capkpi.get_doc(
					{
						"idx": 0,
						"doctype": "Item Barcode",
						"barcode": barcode,
						"parenttype": "Item",
						"parent": item.name,
						"parentfield": "barcodes",
					}
				).insert()
			except (capkpi.DuplicateEntryError, capkpi.UniqueValidationError):
				continue
