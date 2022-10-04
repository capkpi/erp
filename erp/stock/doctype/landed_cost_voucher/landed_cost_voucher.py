# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.model.meta import get_field_precision
from capkpi.utils import flt

import erp
from erp.controllers.taxes_and_totals import init_landed_taxes_and_totals
from erp.stock.doctype.serial_no.serial_no import get_serial_nos


class LandedCostVoucher(Document):
	@capkpi.whitelist()
	def get_items_from_purchase_receipts(self):
		self.set("items", [])
		for pr in self.get("purchase_receipts"):
			if pr.receipt_document_type and pr.receipt_document:
				pr_items = capkpi.db.sql(
					"""select pr_item.item_code, pr_item.description,
					pr_item.qty, pr_item.base_rate, pr_item.base_amount, pr_item.name,
					pr_item.cost_center, pr_item.is_fixed_asset
					from `tab{doctype} Item` pr_item where parent = %s
					and exists(select name from tabItem
						where name = pr_item.item_code and (is_stock_item = 1 or is_fixed_asset=1))
					""".format(
						doctype=pr.receipt_document_type
					),
					pr.receipt_document,
					as_dict=True,
				)

				for d in pr_items:
					item = self.append("items")
					item.item_code = d.item_code
					item.description = d.description
					item.qty = d.qty
					item.rate = d.base_rate
					item.cost_center = d.cost_center or erp.get_default_cost_center(self.company)
					item.amount = d.base_amount
					item.receipt_document_type = pr.receipt_document_type
					item.receipt_document = pr.receipt_document
					item.purchase_receipt_item = d.name
					item.is_fixed_asset = d.is_fixed_asset

	def validate(self):
		self.check_mandatory()
		self.validate_receipt_documents()
		init_landed_taxes_and_totals(self)
		self.set_total_taxes_and_charges()
		if not self.get("items"):
			self.get_items_from_purchase_receipts()

		self.set_applicable_charges_on_item()
		self.validate_applicable_charges_for_item()

	def check_mandatory(self):
		if not self.get("purchase_receipts"):
			capkpi.throw(_("Please enter Receipt Document"))

	def validate_receipt_documents(self):
		receipt_documents = []

		for d in self.get("purchase_receipts"):
			docstatus = capkpi.db.get_value(d.receipt_document_type, d.receipt_document, "docstatus")
			if docstatus != 1:
				msg = (
					f"Row {d.idx}: {d.receipt_document_type} {capkpi.bold(d.receipt_document)} must be submitted"
				)
				capkpi.throw(_(msg), title=_("Invalid Document"))

			if d.receipt_document_type == "Purchase Invoice":
				update_stock = capkpi.db.get_value(d.receipt_document_type, d.receipt_document, "update_stock")
				if not update_stock:
					msg = _("Row {0}: Purchase Invoice {1} has no stock impact.").format(
						d.idx, capkpi.bold(d.receipt_document)
					)
					msg += "<br>" + _(
						"Please create Landed Cost Vouchers against Invoices that have 'Update Stock' enabled."
					)
					capkpi.throw(msg, title=_("Incorrect Invoice"))

			receipt_documents.append(d.receipt_document)

		for item in self.get("items"):
			if not item.receipt_document:
				capkpi.throw(_("Item must be added using 'Get Items from Purchase Receipts' button"))

			elif item.receipt_document not in receipt_documents:
				capkpi.throw(
					_("Item Row {0}: {1} {2} does not exist in above '{1}' table").format(
						item.idx, item.receipt_document_type, item.receipt_document
					)
				)

			if not item.cost_center:
				capkpi.throw(
					_("Row {0}: Cost center is required for an item {1}").format(item.idx, item.item_code)
				)

	def set_total_taxes_and_charges(self):
		self.total_taxes_and_charges = sum(flt(d.base_amount) for d in self.get("taxes"))

	def set_applicable_charges_on_item(self):
		if self.get("taxes") and self.distribute_charges_based_on != "Distribute Manually":
			total_item_cost = 0.0
			total_charges = 0.0
			item_count = 0
			based_on_field = capkpi.scrub(self.distribute_charges_based_on)

			for item in self.get("items"):
				total_item_cost += item.get(based_on_field)

			for item in self.get("items"):
				item.applicable_charges = flt(
					flt(item.get(based_on_field)) * (flt(self.total_taxes_and_charges) / flt(total_item_cost)),
					item.precision("applicable_charges"),
				)
				total_charges += item.applicable_charges
				item_count += 1

			if total_charges != self.total_taxes_and_charges:
				diff = self.total_taxes_and_charges - total_charges
				self.get("items")[item_count - 1].applicable_charges += diff

	def validate_applicable_charges_for_item(self):
		based_on = self.distribute_charges_based_on.lower()

		if based_on != "distribute manually":
			total = sum(flt(d.get(based_on)) for d in self.get("items"))
		else:
			# consider for proportion while distributing manually
			total = sum(flt(d.get("applicable_charges")) for d in self.get("items"))

		if not total:
			capkpi.throw(
				_(
					"Total {0} for all items is zero, may be you should change 'Distribute Charges Based On'"
				).format(based_on)
			)

		total_applicable_charges = sum(flt(d.applicable_charges) for d in self.get("items"))

		precision = get_field_precision(
			capkpi.get_meta("Landed Cost Item").get_field("applicable_charges"),
			currency=capkpi.get_cached_value("Company", self.company, "default_currency"),
		)

		diff = flt(self.total_taxes_and_charges) - flt(total_applicable_charges)
		diff = flt(diff, precision)

		if abs(diff) < (2.0 / (10**precision)):
			self.items[-1].applicable_charges += diff
		else:
			capkpi.throw(
				_(
					"Total Applicable Charges in Purchase Receipt Items table must be same as Total Taxes and Charges"
				)
			)

	def on_submit(self):
		self.update_landed_cost()

	def on_cancel(self):
		self.update_landed_cost()

	def update_landed_cost(self):
		for d in self.get("purchase_receipts"):
			doc = capkpi.get_doc(d.receipt_document_type, d.receipt_document)
			# check if there are {qty} assets created and linked to this receipt document
			self.validate_asset_qty_and_status(d.receipt_document_type, doc)

			# set landed cost voucher amount in pr item
			doc.set_landed_cost_voucher_amount()

			# set valuation amount in pr item
			doc.update_valuation_rate(reset_outgoing_rate=False)

			# db_update will update and save landed_cost_voucher_amount and voucher_amount in PR
			for item in doc.get("items"):
				item.db_update()

			# asset rate will be updated while creating asset gl entries from PI or PY

			# update latest valuation rate in serial no
			self.update_rate_in_serial_no_for_non_asset_items(doc)

		for d in self.get("purchase_receipts"):
			doc = capkpi.get_doc(d.receipt_document_type, d.receipt_document)
			# update stock & gl entries for cancelled state of PR
			doc.docstatus = 2
			doc.update_stock_ledger(allow_negative_stock=True, via_landed_cost_voucher=True)
			doc.make_gl_entries_on_cancel()

			# update stock & gl entries for submit state of PR
			doc.docstatus = 1
			doc.update_stock_ledger(allow_negative_stock=True, via_landed_cost_voucher=True)
			doc.make_gl_entries()
			doc.repost_future_sle_and_gle()

	def validate_asset_qty_and_status(self, receipt_document_type, receipt_document):
		for item in self.get("items"):
			if item.is_fixed_asset:
				receipt_document_type = (
					"purchase_invoice" if item.receipt_document_type == "Purchase Invoice" else "purchase_receipt"
				)
				docs = capkpi.db.get_all(
					"Asset",
					filters={receipt_document_type: item.receipt_document, "item_code": item.item_code},
					fields=["name", "docstatus"],
				)
				if not docs or len(docs) != item.qty:
					capkpi.throw(
						_(
							"There are not enough asset created or linked to {0}. Please create or link {1} Assets with respective document."
						).format(item.receipt_document, item.qty)
					)
				if docs:
					for d in docs:
						if d.docstatus == 1:
							capkpi.throw(
								_(
									"{2} <b>{0}</b> has submitted Assets. Remove Item <b>{1}</b> from table to continue."
								).format(
									item.receipt_document, item.item_code, item.receipt_document_type
								)
							)

	def update_rate_in_serial_no_for_non_asset_items(self, receipt_document):
		for item in receipt_document.get("items"):
			if not item.is_fixed_asset and item.serial_no:
				serial_nos = get_serial_nos(item.serial_no)
				if serial_nos:
					capkpi.db.sql(
						"update `tabSerial No` set purchase_rate=%s where name in ({0})".format(
							", ".join(["%s"] * len(serial_nos))
						),
						tuple([item.valuation_rate] + serial_nos),
					)
