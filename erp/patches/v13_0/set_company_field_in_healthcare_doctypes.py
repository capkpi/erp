import capkpi


def execute():
	company = capkpi.db.get_single_value("Global Defaults", "default_company")
	doctypes = [
		"Clinical Procedure",
		"Inpatient Record",
		"Lab Test",
		"Sample Collection",
		"Patient Appointment",
		"Patient Encounter",
		"Vital Signs",
		"Therapy Session",
		"Therapy Plan",
		"Patient Assessment",
	]
	for entry in doctypes:
		if capkpi.db.exists("DocType", entry):
			capkpi.reload_doc("Healthcare", "doctype", entry)
			capkpi.db.sql(
				"update `tab{dt}` set company = {company} where ifnull(company, '') = ''".format(
					dt=entry, company=capkpi.db.escape(company)
				)
			)
