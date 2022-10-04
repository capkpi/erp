# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import random

import capkpi
from capkpi.desk import query_report

import erp
from erp.stock.doctype.batch.batch import UnableToSelectBatchError
from erp.stock.doctype.delivery_note.delivery_note import make_sales_return
from erp.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
from erp.stock.doctype.serial_no.serial_no import SerialNoQtyError, SerialNoRequiredError
from erp.stock.stock_ledger import NegativeStockError


def work():
	capkpi.set_user(capkpi.db.get_global("demo_manufacturing_user"))

	make_purchase_receipt()
	make_delivery_note()
	make_stock_reconciliation()
	submit_draft_stock_entries()
	make_sales_return_records()
	make_purchase_return_records()


def make_purchase_receipt():
	if random.random() < 0.6:
		from erp.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

		report = "Purchase Order Items To Be Received"
		po_list = list(set([r[0] for r in query_report.run(report)["result"] if r[0] != "Total"]))[
			: random.randint(1, 10)
		]
		for po in po_list:
			pr = capkpi.get_doc(make_purchase_receipt(po))

			if pr.is_subcontracted == "Yes":
				pr.supplier_warehouse = "Supplier - WPL"

			pr.posting_date = capkpi.flags.current_date
			pr.insert()
			try:
				pr.submit()
			except NegativeStockError:
				print("Negative stock for {0}".format(po))
				pass
			capkpi.db.commit()


def make_delivery_note():
	# make purchase requests

	# make delivery notes (if possible)
	if random.random() < 0.6:
		from erp.selling.doctype.sales_order.sales_order import make_delivery_note

		report = "Ordered Items To Be Delivered"
		for so in list(set([r[0] for r in query_report.run(report)["result"] if r[0] != "Total"]))[
			: random.randint(1, 3)
		]:
			dn = capkpi.get_doc(make_delivery_note(so))
			dn.posting_date = capkpi.flags.current_date
			for d in dn.get("items"):
				if not d.expense_account:
					d.expense_account = "Cost of Goods Sold - {0}".format(
						capkpi.get_cached_value("Company", dn.company, "abbr")
					)

			try:
				dn.insert()
				dn.submit()
				capkpi.db.commit()
			except (NegativeStockError, SerialNoRequiredError, SerialNoQtyError, UnableToSelectBatchError):
				capkpi.db.rollback()


def make_stock_reconciliation():
	# random set some items as damaged
	from erp.stock.doctype.stock_reconciliation.stock_reconciliation import (
		EmptyStockReconciliationItemsError,
		OpeningEntryAccountError,
	)

	if random.random() < 0.4:
		stock_reco = capkpi.new_doc("Stock Reconciliation")
		stock_reco.posting_date = capkpi.flags.current_date
		stock_reco.company = erp.get_default_company()
		stock_reco.get_items_for("Stores - WPL")
		if stock_reco.items:
			for item in stock_reco.items:
				if item.qty:
					item.qty = item.qty - round(random.randint(1, item.qty))
			try:
				stock_reco.insert(ignore_permissions=True, ignore_mandatory=True)
				stock_reco.submit()
				capkpi.db.commit()
			except OpeningEntryAccountError:
				capkpi.db.rollback()
			except EmptyStockReconciliationItemsError:
				capkpi.db.rollback()


def submit_draft_stock_entries():
	from erp.stock.doctype.stock_entry.stock_entry import (
		DuplicateEntryForWorkOrderError,
		IncorrectValuationRateError,
		OperationsNotCompleteError,
	)

	# try posting older drafts (if exists)
	capkpi.db.commit()
	for st in capkpi.db.get_values("Stock Entry", {"docstatus": 0}, "name"):
		try:
			ste = capkpi.get_doc("Stock Entry", st[0])
			ste.posting_date = capkpi.flags.current_date
			ste.save()
			ste.submit()
			capkpi.db.commit()
		except (
			NegativeStockError,
			IncorrectValuationRateError,
			DuplicateEntryForWorkOrderError,
			OperationsNotCompleteError,
		):
			capkpi.db.rollback()


def make_sales_return_records():
	if random.random() < 0.1:
		for data in capkpi.get_all("Delivery Note", fields=["name"], filters={"docstatus": 1}):
			if random.random() < 0.1:
				try:
					dn = make_sales_return(data.name)
					dn.insert()
					dn.submit()
					capkpi.db.commit()
				except Exception:
					capkpi.db.rollback()


def make_purchase_return_records():
	if random.random() < 0.1:
		for data in capkpi.get_all("Purchase Receipt", fields=["name"], filters={"docstatus": 1}):
			if random.random() < 0.1:
				try:
					pr = make_purchase_return(data.name)
					pr.insert()
					pr.submit()
					capkpi.db.commit()
				except Exception:
					capkpi.db.rollback()
