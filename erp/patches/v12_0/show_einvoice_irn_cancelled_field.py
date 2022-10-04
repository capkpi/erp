import capkpi


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	irn_cancelled_field = capkpi.db.exists(
		"Custom Field", {"dt": "Sales Invoice", "fieldname": "irn_cancelled"}
	)
	if irn_cancelled_field:
		capkpi.db.set_value("Custom Field", irn_cancelled_field, "depends_on", "eval: doc.irn")
		capkpi.db.set_value("Custom Field", irn_cancelled_field, "read_only", 0)
