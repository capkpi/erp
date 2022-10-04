# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class MaterialRequestItem(Document):
	pass


def on_doctype_update():
	capkpi.db.add_index("Material Request Item", ["item_code", "warehouse"])
