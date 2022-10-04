import capkpi


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	if capkpi.db.exists("Report", "E-Invoice Summary") and not capkpi.db.get_value(
		"Custom Role", dict(report="E-Invoice Summary")
	):
		capkpi.get_doc(
			dict(
				doctype="Custom Role",
				report="E-Invoice Summary",
				roles=[dict(role="Accounts User"), dict(role="Accounts Manager")],
			)
		).insert()
