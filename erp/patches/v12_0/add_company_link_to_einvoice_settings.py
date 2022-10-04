import capkpi


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})

	if not company:
		return

	capkpi.reload_doc("regional", "doctype", "e_invoice_user")
	if not capkpi.db.count("E Invoice User"):
		return

	for creds in capkpi.db.get_all("E Invoice User", fields=["name", "gstin"]):
		company_name = capkpi.db.sql(
			"""
			select dl.link_name from `tabAddress` a, `tabDynamic Link` dl
			where a.gstin = %s and dl.parent = a.name and dl.link_doctype = 'Company'
		""",
			(creds.get("gstin")),
		)
		if company_name and len(company_name) > 0:
			capkpi.db.set_value("E Invoice User", creds.get("name"), "company", company_name[0][0])
