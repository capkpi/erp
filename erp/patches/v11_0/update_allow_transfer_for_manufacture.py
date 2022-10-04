# Copyright (c) 2018, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("stock", "doctype", "item")
	capkpi.db.sql(
		""" update `tabItem` set include_item_in_manufacturing = 1
		where ifnull(is_stock_item, 0) = 1"""
	)

	for doctype in ["BOM Item", "Work Order Item", "BOM Explosion Item"]:
		capkpi.reload_doc("manufacturing", "doctype", capkpi.scrub(doctype))

		capkpi.db.sql(
			""" update `tab{0}` child, tabItem item
			set
				child.include_item_in_manufacturing = 1
			where
				child.item_code = item.name and ifnull(item.is_stock_item, 0) = 1
		""".format(
				doctype
			)
		)
