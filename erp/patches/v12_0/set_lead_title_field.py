import capkpi


def execute():
	capkpi.reload_doc("crm", "doctype", "lead")
	capkpi.db.sql(
		"""
		UPDATE
			`tabLead`
		SET
			title = IF(organization_lead = 1, company_name, lead_name)
	"""
	)
