# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	if capkpi.db.table_exists("Asset Adjustment") and not capkpi.db.table_exists(
		"Asset Value Adjustment"
	):
		capkpi.rename_doc("DocType", "Asset Adjustment", "Asset Value Adjustment", force=True)
		capkpi.reload_doc("assets", "doctype", "asset_value_adjustment")
