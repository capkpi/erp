# Copyright (c) 2018, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.rename_doc("DocType", "Health Insurance", "Employee Health Insurance", force=True)
	capkpi.reload_doc("hr", "doctype", "employee_health_insurance")
