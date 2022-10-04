# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	if capkpi.db.exists("DocType", "Scheduling Tool"):
		capkpi.delete_doc("DocType", "Scheduling Tool", ignore_permissions=True)
