# Copyright(c) 2020, CapKPI Technologies Pvt.Ltd.and Contributors
# License: GNU General Public License v3.See license.txt


import capkpi


def execute():
	capkpi.reload_doc("stock", "doctype", "stock_entry")
	if capkpi.db.has_column("Stock Entry", "add_to_transit"):
		capkpi.db.sql(
			"""
            UPDATE `tabStock Entry` SET
            stock_entry_type = 'Material Transfer',
            purpose = 'Material Transfer',
            add_to_transit = 1 WHERE stock_entry_type = 'Send to Warehouse'
            """
		)

		capkpi.db.sql(
			"""UPDATE `tabStock Entry` SET
            stock_entry_type = 'Material Transfer',
            purpose = 'Material Transfer'
            WHERE stock_entry_type = 'Receive at Warehouse'
            """
		)

		capkpi.reload_doc("stock", "doctype", "warehouse_type")
		if not capkpi.db.exists("Warehouse Type", "Transit"):
			doc = capkpi.new_doc("Warehouse Type")
			doc.name = "Transit"
			doc.insert()

		capkpi.reload_doc("stock", "doctype", "stock_entry_type")
		capkpi.delete_doc_if_exists("Stock Entry Type", "Send to Warehouse")
		capkpi.delete_doc_if_exists("Stock Entry Type", "Receive at Warehouse")
