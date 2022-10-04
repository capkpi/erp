import capkpi


def execute():
	capkpi.reload_doc("manufacturing", "doctype", "workstation")

	capkpi.db.sql(
		""" UPDATE `tabWorkstation`
        SET production_capacity = 1 """
	)
