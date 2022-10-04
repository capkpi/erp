# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.model.document import Document


class PurchaseOrderItem(Document):
	pass


def on_doctype_update():
	capkpi.db.add_index("Purchase Order Item", ["item_code", "warehouse"])
