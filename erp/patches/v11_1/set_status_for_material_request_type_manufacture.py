import capkpi


def execute():
	capkpi.db.sql(
		"""
		update `tabMaterial Request`
		set status='Manufactured'
		where docstatus=1 and material_request_type='Manufacture' and per_ordered=100 and status != 'Stopped'
	"""
	)
