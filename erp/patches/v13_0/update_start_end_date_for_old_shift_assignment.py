# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("hr", "doctype", "shift_assignment")
	if capkpi.db.has_column("Shift Assignment", "date"):
		capkpi.db.sql(
			"""update `tabShift Assignment`
            set end_date=date, start_date=date
            where date IS NOT NULL and start_date IS NULL and end_date IS NULL;"""
		)
