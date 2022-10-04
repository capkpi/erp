# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class SupplierScorecardStanding(Document):
	pass


@capkpi.whitelist()
def get_scoring_standing(standing_name):
	standing = capkpi.get_doc("Supplier Scorecard Standing", standing_name)

	return standing


@capkpi.whitelist()
def get_standings_list():
	standings = capkpi.db.sql(
		"""
		SELECT
			scs.name
		FROM
			`tabSupplier Scorecard Standing` scs""",
		{},
		as_dict=1,
	)

	return standings
