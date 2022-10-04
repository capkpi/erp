# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import random

import capkpi
from capkpi.desk import query_report
from capkpi.utils import random_string
from capkpi.utils.make_random import get_random

import erp
from erp.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
from erp.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erp.accounts.doctype.payment_request.payment_request import (
	make_payment_entry,
	make_payment_request,
)
from erp.demo.user.sales import make_sales_order
from erp.selling.doctype.sales_order.sales_order import make_sales_invoice
from erp.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice


def work():
	capkpi.set_user(capkpi.db.get_global("demo_accounts_user"))

	if random.random() <= 0.6:
		report = "Ordered Items to be Billed"
		for so in list(set([r[0] for r in query_report.run(report)["result"] if r[0] != "Total"]))[
			: random.randint(1, 5)
		]:
			try:
				si = capkpi.get_doc(make_sales_invoice(so))
				si.posting_date = capkpi.flags.current_date
				for d in si.get("items"):
					if not d.income_account:
						d.income_account = "Sales - {}".format(
							capkpi.get_cached_value("Company", si.company, "abbr")
						)
				si.insert()
				si.submit()
				capkpi.db.commit()
			except capkpi.ValidationError:
				pass

	if random.random() <= 0.6:
		report = "Received Items to be Billed"
		for pr in list(set([r[0] for r in query_report.run(report)["result"] if r[0] != "Total"]))[
			: random.randint(1, 5)
		]:
			try:
				pi = capkpi.get_doc(make_purchase_invoice(pr))
				pi.posting_date = capkpi.flags.current_date
				pi.bill_no = random_string(6)
				pi.insert()
				pi.submit()
				capkpi.db.commit()
			except capkpi.ValidationError:
				pass

	if random.random() < 0.5:
		make_payment_entries("Sales Invoice", "Accounts Receivable")

	if random.random() < 0.5:
		make_payment_entries("Purchase Invoice", "Accounts Payable")

	if random.random() < 0.4:
		# make payment request against sales invoice
		sales_invoice_name = get_random("Sales Invoice", filters={"docstatus": 1})
		if sales_invoice_name:
			si = capkpi.get_doc("Sales Invoice", sales_invoice_name)
			if si.outstanding_amount > 0:
				payment_request = make_payment_request(
					dt="Sales Invoice",
					dn=si.name,
					recipient_id=si.contact_email,
					submit_doc=True,
					mute_email=True,
					use_dummy_message=True,
				)

				payment_entry = capkpi.get_doc(make_payment_entry(payment_request.name))
				payment_entry.posting_date = capkpi.flags.current_date
				payment_entry.submit()

	make_pos_invoice()


def make_payment_entries(ref_doctype, report):

	outstanding_invoices = capkpi.get_all(
		ref_doctype,
		fields=["name"],
		filters={"company": erp.get_default_company(), "outstanding_amount": (">", 0.0)},
	)

	# make Payment Entry
	for inv in outstanding_invoices[: random.randint(1, 2)]:
		pe = get_payment_entry(ref_doctype, inv.name)
		pe.posting_date = capkpi.flags.current_date
		pe.reference_no = random_string(6)
		pe.reference_date = capkpi.flags.current_date
		pe.insert()
		pe.submit()
		capkpi.db.commit()
		outstanding_invoices.remove(inv)

	# make payment via JV
	for inv in outstanding_invoices[:1]:
		jv = capkpi.get_doc(get_payment_entry_against_invoice(ref_doctype, inv.name))
		jv.posting_date = capkpi.flags.current_date
		jv.cheque_no = random_string(6)
		jv.cheque_date = capkpi.flags.current_date
		jv.insert()
		jv.submit()
		capkpi.db.commit()


def make_pos_invoice():
	make_sales_order()

	for data in capkpi.get_all("Sales Order", fields=["name"], filters=[["per_billed", "<", "100"]]):
		si = capkpi.get_doc(make_sales_invoice(data.name))
		si.is_pos = 1
		si.posting_date = capkpi.flags.current_date
		for d in si.get("items"):
			if not d.income_account:
				d.income_account = "Sales - {}".format(capkpi.get_cached_value("Company", si.company, "abbr"))
		si.set_missing_values()
		make_payment_entries_for_pos_invoice(si)
		si.insert()
		si.submit()


def make_payment_entries_for_pos_invoice(si):
	for data in si.payments:
		data.amount = si.outstanding_amount
		return