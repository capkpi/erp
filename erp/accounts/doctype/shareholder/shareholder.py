# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from capkpi.model.document import Document


class Shareholder(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def on_trash(self):
		delete_contact_and_address("Shareholder", self.name)

	def before_save(self):
		for entry in self.share_balance:
			entry.amount = entry.no_of_shares * entry.rate
