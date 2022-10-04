# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from capkpi.model.document import Document


class Bank(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def on_trash(self):
		delete_contact_and_address("Bank", self.name)
