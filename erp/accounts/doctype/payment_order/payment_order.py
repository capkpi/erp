# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import nowdate

from erp.accounts.party import get_party_account


class PaymentOrder(Document):
	def on_submit(self):
		self.update_payment_status()

	def on_cancel(self):
		self.update_payment_status(cancel=True)

	def update_payment_status(self, cancel=False):
		status = "Payment Ordered"
		if cancel:
			status = "Initiated"

		if self.payment_order_type == "Payment Request":
			ref_field = "status"
			ref_doc_field = capkpi.scrub(self.payment_order_type)
		else:
			ref_field = "payment_order_status"
			ref_doc_field = "reference_name"

		for d in self.references:
			capkpi.db.set_value(self.payment_order_type, d.get(ref_doc_field), ref_field, status)


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_mop_query(doctype, txt, searchfield, start, page_len, filters):
	return capkpi.db.sql(
		""" select mode_of_payment from `tabPayment Order Reference`
		where parent = %(parent)s and mode_of_payment like %(txt)s
		limit %(start)s, %(page_len)s""",
		{"parent": filters.get("parent"), "start": start, "page_len": page_len, "txt": "%%%s%%" % txt},
	)


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_supplier_query(doctype, txt, searchfield, start, page_len, filters):
	return capkpi.db.sql(
		""" select supplier from `tabPayment Order Reference`
		where parent = %(parent)s and supplier like %(txt)s and
		(payment_reference is null or payment_reference='')
		limit %(start)s, %(page_len)s""",
		{"parent": filters.get("parent"), "start": start, "page_len": page_len, "txt": "%%%s%%" % txt},
	)


@capkpi.whitelist()
def make_payment_records(name, supplier, mode_of_payment=None):
	doc = capkpi.get_doc("Payment Order", name)
	make_journal_entry(doc, supplier, mode_of_payment)


def make_journal_entry(doc, supplier, mode_of_payment=None):
	je = capkpi.new_doc("Journal Entry")
	je.payment_order = doc.name
	je.posting_date = nowdate()
	mode_of_payment_type = capkpi._dict(
		capkpi.get_all("Mode of Payment", fields=["name", "type"], as_list=1)
	)

	je.voucher_type = "Bank Entry"
	if mode_of_payment and mode_of_payment_type.get(mode_of_payment) == "Cash":
		je.voucher_type = "Cash Entry"

	paid_amt = 0
	party_account = get_party_account("Supplier", supplier, doc.company)
	for d in doc.references:
		if d.supplier == supplier and (not mode_of_payment or mode_of_payment == d.mode_of_payment):
			je.append(
				"accounts",
				{
					"account": party_account,
					"debit_in_account_currency": d.amount,
					"party_type": "Supplier",
					"party": supplier,
					"reference_type": d.reference_doctype,
					"reference_name": d.reference_name,
				},
			)

			paid_amt += d.amount

	je.append("accounts", {"account": doc.account, "credit_in_account_currency": paid_amt})

	je.flags.ignore_mandatory = True
	je.save()
	capkpi.msgprint(_("{0} {1} created").format(je.doctype, je.name))