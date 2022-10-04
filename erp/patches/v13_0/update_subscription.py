# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from six import iteritems


def execute():

	capkpi.reload_doc("accounts", "doctype", "subscription")
	capkpi.reload_doc("accounts", "doctype", "subscription_invoice")
	capkpi.reload_doc("accounts", "doctype", "subscription_plan")

	if capkpi.db.has_column("Subscription", "customer"):
		capkpi.db.sql(
			"""
			UPDATE `tabSubscription`
			SET
				start_date = start,
				party_type = 'Customer',
				party = customer,
				sales_tax_template = tax_template
			WHERE IFNULL(party,'') = ''
		"""
		)

	capkpi.db.sql(
		"""
		UPDATE `tabSubscription Invoice`
		SET document_type = 'Sales Invoice'
		WHERE IFNULL(document_type, '') = ''
	"""
	)

	price_determination_map = {
		"Fixed rate": "Fixed Rate",
		"Based on price list": "Based On Price List",
	}

	for key, value in iteritems(price_determination_map):
		capkpi.db.sql(
			"""
			UPDATE `tabSubscription Plan`
			SET price_determination = %s
			WHERE price_determination = %s
		""",
			(value, key),
		)
