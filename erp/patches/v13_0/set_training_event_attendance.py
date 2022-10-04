import capkpi


def execute():
	capkpi.reload_doc("hr", "doctype", "training_event")
	capkpi.reload_doc("hr", "doctype", "training_event_employee")

	capkpi.db.sql("update `tabTraining Event Employee` set `attendance` = 'Present'")
	capkpi.db.sql(
		"update `tabTraining Event Employee` set `is_mandatory` = 1 where `attendance` = 'Mandatory'"
	)
