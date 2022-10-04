# Copyright (c) 2018, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.model.utils.rename_field import rename_field


def execute():
	capkpi.reload_doc("manufacturing", "doctype", "manufacturing_settings")
	rename_field(
		"Manufacturing Settings",
		"over_production_allowance_percentage",
		"overproduction_percentage_for_sales_order",
	)
