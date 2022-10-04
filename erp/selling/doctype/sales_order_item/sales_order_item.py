# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.model.document import Document


class SalesOrderItem(Document):
	pass


def on_doctype_update():
	capkpi.db.add_index("Sales Order Item", ["item_code", "warehouse"])
