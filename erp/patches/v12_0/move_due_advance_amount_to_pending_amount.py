# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	"""Move from due_advance_amount to pending_amount"""

	if capkpi.db.has_column("Employee Advance", "due_advance_amount"):
		capkpi.db.sql(""" UPDATE `tabEmployee Advance` SET pending_amount=due_advance_amount """)
