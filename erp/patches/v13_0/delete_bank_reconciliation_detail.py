# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():

	if capkpi.db.exists("DocType", "Bank Reconciliation Detail") and capkpi.db.exists(
		"DocType", "Bank Clearance Detail"
	):

		capkpi.delete_doc("DocType", "Bank Reconciliation Detail", force=1)
