# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():

	capkpi.reload_doc("accounts", "doctype", "bank_account")
	capkpi.reload_doc("accounts", "doctype", "bank")

	if capkpi.db.has_column("Bank", "branch_code") and capkpi.db.has_column(
		"Bank Account", "branch_code"
	):
		capkpi.db.sql(
			"""UPDATE `tabBank` b, `tabBank Account` ba
			SET ba.branch_code = b.branch_code
			WHERE ba.bank = b.name AND
			ifnull(b.branch_code, '') != '' AND ifnull(ba.branch_code, '') = ''"""
		)
