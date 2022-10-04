# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

from erp.setup.install import create_default_cash_flow_mapper_templates


def execute():
	capkpi.reload_doc("accounts", "doctype", capkpi.scrub("Cash Flow Mapping"))
	capkpi.reload_doc("accounts", "doctype", capkpi.scrub("Cash Flow Mapper"))
	capkpi.reload_doc("accounts", "doctype", capkpi.scrub("Cash Flow Mapping Template Details"))

	create_default_cash_flow_mapper_templates()
