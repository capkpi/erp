# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

from erp.regional.united_arab_emirates.setup import make_custom_fields


def execute():
	company = capkpi.get_all(
		"Company", filters={"country": ["in", ["Saudi Arabia", "United Arab Emirates"]]}
	)
	if not company:
		return

	capkpi.reload_doc("accounts", "doctype", "pos_invoice")
	capkpi.reload_doc("accounts", "doctype", "pos_invoice_item")

	make_custom_fields()
