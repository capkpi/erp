# Copyright (c) 2020, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi

from erp.regional.south_africa.setup import add_permissions, make_custom_fields


def execute():
	company = capkpi.get_all("Company", filters={"country": "South Africa"})
	if not company:
		return

	capkpi.reload_doc("regional", "doctype", "south_africa_vat_settings")
	capkpi.reload_doc("regional", "report", "vat_audit_report")
	capkpi.reload_doc("accounts", "doctype", "south_africa_vat_account")

	make_custom_fields()
	add_permissions()
