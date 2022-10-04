# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import capkpi
from capkpi import _
from capkpi.model.document import Document


class PartySpecificItem(Document):
	def validate(self):
		exists = capkpi.db.exists(
			{
				"doctype": "Party Specific Item",
				"party_type": self.party_type,
				"party": self.party,
				"restrict_based_on": self.restrict_based_on,
				"based_on": self.based_on_value,
			}
		)
		if exists:
			capkpi.throw(_("This item filter has already been applied for the {0}").format(self.party_type))
