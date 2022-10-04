import capkpi


def execute():

	capkpi.reload_doctype("Opportunity")
	if capkpi.db.has_column("Opportunity", "enquiry_from"):
		capkpi.db.sql(
			""" UPDATE `tabOpportunity` set opportunity_from = enquiry_from
			where ifnull(opportunity_from, '') = '' and ifnull(enquiry_from, '') != ''"""
		)

	if capkpi.db.has_column("Opportunity", "lead") and capkpi.db.has_column(
		"Opportunity", "enquiry_from"
	):
		capkpi.db.sql(
			""" UPDATE `tabOpportunity` set party_name = lead
			where enquiry_from = 'Lead' and ifnull(party_name, '') = '' and ifnull(lead, '') != ''"""
		)

	if capkpi.db.has_column("Opportunity", "customer") and capkpi.db.has_column(
		"Opportunity", "enquiry_from"
	):
		capkpi.db.sql(
			""" UPDATE `tabOpportunity` set party_name = customer
			 where enquiry_from = 'Customer' and ifnull(party_name, '') = '' and ifnull(customer, '') != ''"""
		)
