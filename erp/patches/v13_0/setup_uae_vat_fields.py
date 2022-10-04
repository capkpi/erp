# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi

from erp.regional.united_arab_emirates.setup import setup


def execute():
	company = capkpi.get_all("Company", filters={"country": "United Arab Emirates"})
	if not company:
		return

	capkpi.reload_doc("regional", "report", "uae_vat_201")
	capkpi.reload_doc("regional", "doctype", "uae_vat_settings")
	capkpi.reload_doc("regional", "doctype", "uae_vat_account")

	setup()
