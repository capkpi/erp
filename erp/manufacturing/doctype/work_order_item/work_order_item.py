# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class WorkOrderItem(Document):
	pass


def on_doctype_update():
	capkpi.db.add_index("Work Order Item", ["item_code", "source_warehouse"])
