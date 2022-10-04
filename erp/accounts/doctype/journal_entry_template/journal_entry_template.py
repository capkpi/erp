# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class JournalEntryTemplate(Document):
	pass


@capkpi.whitelist()
def get_naming_series():
	return capkpi.get_meta("Journal Entry").get_field("naming_series").options
