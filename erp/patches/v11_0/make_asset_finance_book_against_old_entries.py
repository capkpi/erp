# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("assets", "doctype", "asset_finance_book")
	capkpi.reload_doc("assets", "doctype", "depreciation_schedule")
	capkpi.reload_doc("assets", "doctype", "asset_category")
	capkpi.reload_doc("assets", "doctype", "asset")
	capkpi.reload_doc("assets", "doctype", "asset_movement")
	capkpi.reload_doc("assets", "doctype", "asset_category_account")

	if capkpi.db.has_column("Asset", "warehouse"):
		capkpi.db.sql(
			""" update `tabAsset` ast, `tabWarehouse` wh
			set ast.location = wh.warehouse_name where ast.warehouse = wh.name"""
		)

		for d in capkpi.get_all("Asset"):
			doc = capkpi.get_doc("Asset", d.name)
			if doc.calculate_depreciation:
				fb = doc.append(
					"finance_books",
					{
						"depreciation_method": doc.depreciation_method,
						"total_number_of_depreciations": doc.total_number_of_depreciations,
						"frequency_of_depreciation": doc.frequency_of_depreciation,
						"depreciation_start_date": doc.next_depreciation_date,
						"expected_value_after_useful_life": doc.expected_value_after_useful_life,
						"value_after_depreciation": doc.value_after_depreciation,
					},
				)

				fb.db_update()

		capkpi.db.sql(
			""" update `tabDepreciation Schedule` ds, `tabAsset` ast
			set ds.depreciation_method = ast.depreciation_method, ds.finance_book_id = 1 where ds.parent = ast.name """
		)

		for category in capkpi.get_all("Asset Category"):
			asset_category_doc = capkpi.get_doc("Asset Category", category)
			row = asset_category_doc.append(
				"finance_books",
				{
					"depreciation_method": asset_category_doc.depreciation_method,
					"total_number_of_depreciations": asset_category_doc.total_number_of_depreciations,
					"frequency_of_depreciation": asset_category_doc.frequency_of_depreciation,
				},
			)

			row.db_update()
