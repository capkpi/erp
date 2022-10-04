# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doctype("Quotation")
	capkpi.db.sql(""" UPDATE `tabQuotation` set party_name = lead WHERE quotation_to = 'Lead' """)
	capkpi.db.sql(
		""" UPDATE `tabQuotation` set party_name = customer WHERE quotation_to = 'Customer' """
	)

	capkpi.reload_doctype("Opportunity")
	capkpi.db.sql(
		""" UPDATE `tabOpportunity` set party_name = lead WHERE opportunity_from = 'Lead' """
	)
	capkpi.db.sql(
		""" UPDATE `tabOpportunity` set party_name = customer WHERE opportunity_from = 'Customer' """
	)
