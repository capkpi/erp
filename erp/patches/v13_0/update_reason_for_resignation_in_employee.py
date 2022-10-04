# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("hr", "doctype", "employee")

	if capkpi.db.has_column("Employee", "reason_for_resignation"):
		capkpi.db.sql(
			""" UPDATE `tabEmployee`
            SET reason_for_leaving = reason_for_resignation
            WHERE status = 'Left' and reason_for_leaving is null and reason_for_resignation is not null
        """
		)
