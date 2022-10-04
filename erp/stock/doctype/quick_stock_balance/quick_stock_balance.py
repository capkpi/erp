# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document

from erp.stock.utils import get_stock_balance, get_stock_value_on


class QuickStockBalance(Document):
	pass


@capkpi.whitelist()
def get_stock_item_details(warehouse, date, item=None, barcode=None):
	out = {}
	if barcode:
		out["item"] = capkpi.db.get_value(
			"Item Barcode", filters={"barcode": barcode}, fieldname=["parent"]
		)
		if not out["item"]:
			capkpi.throw(_("Invalid Barcode. There is no Item attached to this barcode."))
	else:
		out["item"] = item

	barcodes = capkpi.db.get_values(
		"Item Barcode", filters={"parent": out["item"]}, fieldname=["barcode"]
	)

	out["barcodes"] = [x[0] for x in barcodes]
	out["qty"] = get_stock_balance(out["item"], warehouse, date)
	out["value"] = get_stock_value_on(warehouse, date, out["item"])
	out["image"] = capkpi.db.get_value("Item", filters={"name": out["item"]}, fieldname=["image"])
	return out
