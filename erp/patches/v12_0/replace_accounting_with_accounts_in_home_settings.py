import capkpi


def execute():
	capkpi.db.sql(
		"""UPDATE `tabUser` SET `home_settings` = REPLACE(`home_settings`, 'Accounting', 'Accounts')"""
	)
	capkpi.cache().delete_key("home_settings")
