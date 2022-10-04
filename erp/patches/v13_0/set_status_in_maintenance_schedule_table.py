import capkpi


def execute():
	capkpi.reload_doc("maintenance", "doctype", "Maintenance Schedule Detail")
	capkpi.db.sql(
		"""
		UPDATE `tabMaintenance Schedule Detail`
		SET completion_status = 'Pending'
		WHERE docstatus < 2
	"""
	)
