# Copyright (c) 2018, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	if capkpi.db.table_exists("Bank Reconciliation"):
		capkpi.rename_doc("DocType", "Bank Reconciliation", "Bank Clearance", force=True)
		capkpi.reload_doc("Accounts", "doctype", "Bank Clearance")

		capkpi.rename_doc("DocType", "Bank Reconciliation Detail", "Bank Clearance Detail", force=True)
		capkpi.reload_doc("Accounts", "doctype", "Bank Clearance Detail")
