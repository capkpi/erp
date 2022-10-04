import capkpi


def execute():
	if capkpi.db.exists("DocType", "Member"):
		capkpi.reload_doc("Non Profit", "doctype", "Member")

		if capkpi.db.has_column("Member", "subscription_activated"):
			capkpi.db.sql(
				'UPDATE `tabMember` SET subscription_status = "Active" WHERE subscription_activated = 1'
			)
			capkpi.db.sql_ddl("ALTER table `tabMember` DROP COLUMN subscription_activated")
