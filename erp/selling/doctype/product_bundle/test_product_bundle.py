# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi

test_records = capkpi.get_test_records("Product Bundle")


def make_product_bundle(parent, items, qty=None):
	if capkpi.db.exists("Product Bundle", parent):
		return capkpi.get_doc("Product Bundle", parent)

	product_bundle = capkpi.get_doc({"doctype": "Product Bundle", "new_item_code": parent})

	for item in items:
		product_bundle.append("items", {"item_code": item, "qty": qty or 1})

	product_bundle.insert()

	return product_bundle
