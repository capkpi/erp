# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.contacts.address_and_contact import load_address_and_contact
from capkpi.model.document import Document


class Volunteer(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
