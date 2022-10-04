# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("payroll", "doctype", "gratuity_rule")
	capkpi.reload_doc("payroll", "doctype", "gratuity_rule_slab")
	capkpi.reload_doc("payroll", "doctype", "gratuity_applicable_component")
	if capkpi.db.exists("Company", {"country": "India"}):
		from erp.regional.india.setup import create_gratuity_rule

		create_gratuity_rule()
	if capkpi.db.exists("Company", {"country": "United Arab Emirates"}):
		from erp.regional.united_arab_emirates.setup import create_gratuity_rule

		create_gratuity_rule()
