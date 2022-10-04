import capkpi


def execute():
	capkpi.reload_doc("projects", "doctype", "project")

	capkpi.db.sql(
		"""UPDATE `tabProject`
		SET
			naming_series = 'PROJ-.####'
		WHERE
			naming_series is NULL"""
	)
