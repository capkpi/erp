import capkpi


def execute():
	"""Remove has_variants and attribute fields from item variant settings."""
	capkpi.reload_doc("stock", "doctype", "Item Variant Settings")

	capkpi.db.sql(
		"""delete from `tabVariant Field`
			where field_name in ('attributes', 'has_variants')"""
	)
