import capkpi


def execute():
	capkpi.reload_doc("Hub Node", "doctype", "Hub Tracked Item")
	if not capkpi.db.a_row_exists("Hub Tracked Item"):
		return

	capkpi.db.sql(
		"""
		Update `tabHub Tracked Item`
		SET published = 1
	"""
	)
