# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi import _
from capkpi.desk.search import sanitize_searchfield
from capkpi.model.document import Document


class BankGuarantee(Document):
	def validate(self):
		if not (self.customer or self.supplier):
			capkpi.throw(_("Select the customer or supplier."))

	def on_submit(self):
		if not self.bank_guarantee_number:
			capkpi.throw(_("Enter the Bank Guarantee Number before submittting."))
		if not self.name_of_beneficiary:
			capkpi.throw(_("Enter the name of the Beneficiary before submittting."))
		if not self.bank:
			capkpi.throw(_("Enter the name of the bank or lending institution before submittting."))


@capkpi.whitelist()
def get_vouchar_detials(column_list, doctype, docname):
	column_list = json.loads(column_list)
	for col in column_list:
		sanitize_searchfield(col)
	return capkpi.db.sql(
		""" select {columns} from `tab{doctype}` where name=%s""".format(
			columns=", ".join(column_list), doctype=doctype
		),
		docname,
		as_dict=1,
	)[0]
