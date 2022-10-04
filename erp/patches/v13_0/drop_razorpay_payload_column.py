import capkpi


def execute():
	if capkpi.db.exists("DocType", "Membership"):
		if "webhook_payload" in capkpi.db.get_table_columns("Membership"):
			capkpi.db.sql("alter table `tabMembership` drop column webhook_payload")
