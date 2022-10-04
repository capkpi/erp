import capkpi


def execute():
	if capkpi.db.exists("DocType", "Leave Type"):
		if "max_days_allowed" in capkpi.db.get_table_columns("Leave Type"):
			capkpi.db.sql("alter table `tabLeave Type` drop column max_days_allowed")
