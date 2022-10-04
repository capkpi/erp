# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json
import unittest
from collections import defaultdict

import capkpi
from capkpi.tests.utils import CapKPITestCase, change_settings
from capkpi.utils import add_days, cint, cstr, flt, today
from pypika import functions as fn
from six import iteritems

import erp
from erp.accounts.doctype.account.test_account import get_inventory_account
from erp.controllers.buying_controller import QtyMismatchError
from erp.stock.doctype.item.test_item import create_item, make_item
from erp.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
from erp.stock.doctype.serial_no.serial_no import SerialNoDuplicateError, get_serial_nos
from erp.stock.doctype.warehouse.test_warehouse import create_warehouse
from erp.stock.stock_ledger import SerialNoExistsInFutureTransaction


class TestPurchaseReceipt(CapKPITestCase):
	def setUp(self):
		capkpi.db.set_value("Buying Settings", None, "allow_multiple_items", 1)

	def test_purchase_receipt_received_qty(self):
		"""
		1. Test if received qty is validated against accepted + rejected
		2. Test if received qty is auto set on save
		"""
		pr = make_purchase_receipt(
			qty=1, rejected_qty=1, received_qty=3, item_code="_Test Item Home Desktop 200", do_not_save=True
		)
		self.assertRaises(QtyMismatchError, pr.save)

		pr.items[0].received_qty = 0
		pr.save()
		self.assertEqual(pr.items[0].received_qty, 2)

		# teardown
		pr.delete()

	def test_reverse_purchase_receipt_sle(self):

		pr = make_purchase_receipt(qty=0.5, item_code="_Test Item Home Desktop 200")

		sl_entry = capkpi.db.get_all(
			"Stock Ledger Entry",
			{"voucher_type": "Purchase Receipt", "voucher_no": pr.name},
			["actual_qty"],
		)

		self.assertEqual(len(sl_entry), 1)
		self.assertEqual(sl_entry[0].actual_qty, 0.5)

		pr.cancel()

		sl_entry_cancelled = capkpi.db.get_all(
			"Stock Ledger Entry",
			{"voucher_type": "Purchase Receipt", "voucher_no": pr.name},
			["actual_qty"],
			order_by="creation",
		)

		self.assertEqual(len(sl_entry_cancelled), 2)
		self.assertEqual(sl_entry_cancelled[1].actual_qty, -0.5)

	def test_make_purchase_invoice(self):
		if not capkpi.db.exists(
			"Payment Terms Template", "_Test Payment Terms Template For Purchase Invoice"
		):
			capkpi.get_doc(
				{
					"doctype": "Payment Terms Template",
					"template_name": "_Test Payment Terms Template For Purchase Invoice",
					"allocate_payment_based_on_payment_terms": 1,
					"terms": [
						{
							"doctype": "Payment Terms Template Detail",
							"invoice_portion": 50.00,
							"credit_days_based_on": "Day(s) after invoice date",
							"credit_days": 00,
						},
						{
							"doctype": "Payment Terms Template Detail",
							"invoice_portion": 50.00,
							"credit_days_based_on": "Day(s) after invoice date",
							"credit_days": 30,
						},
					],
				}
			).insert()

		template = capkpi.db.get_value(
			"Payment Terms Template", "_Test Payment Terms Template For Purchase Invoice"
		)
		old_template_in_supplier = capkpi.db.get_value("Supplier", "_Test Supplier", "payment_terms")
		capkpi.db.set_value("Supplier", "_Test Supplier", "payment_terms", template)

		pr = make_purchase_receipt(do_not_save=True)
		self.assertRaises(capkpi.ValidationError, make_purchase_invoice, pr.name)
		pr.submit()

		pi = make_purchase_invoice(pr.name)

		self.assertEqual(pi.doctype, "Purchase Invoice")
		self.assertEqual(len(pi.get("items")), len(pr.get("items")))

		# test maintaining same rate throughout purchade cycle
		pi.get("items")[0].rate = 200
		self.assertRaises(capkpi.ValidationError, capkpi.get_doc(pi).submit)

		# test if payment terms are fetched and set in PI
		self.assertEqual(pi.payment_terms_template, template)
		self.assertEqual(pi.payment_schedule[0].payment_amount, flt(pi.grand_total) / 2)
		self.assertEqual(pi.payment_schedule[0].invoice_portion, 50)
		self.assertEqual(pi.payment_schedule[1].payment_amount, flt(pi.grand_total) / 2)
		self.assertEqual(pi.payment_schedule[1].invoice_portion, 50)

		# teardown
		pi.delete()  # draft PI
		pr.cancel()
		capkpi.db.set_value("Supplier", "_Test Supplier", "payment_terms", old_template_in_supplier)
		capkpi.get_doc(
			"Payment Terms Template", "_Test Payment Terms Template For Purchase Invoice"
		).delete()

	def test_purchase_receipt_no_gl_entry(self):
		from erp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry

		existing_bin_qty, existing_bin_stock_value = capkpi.db.get_value(
			"Bin",
			{"item_code": "_Test Item", "warehouse": "_Test Warehouse - _TC"},
			["actual_qty", "stock_value"],
		)

		if existing_bin_qty < 0:
			make_stock_entry(
				item_code="_Test Item", target="_Test Warehouse - _TC", qty=abs(existing_bin_qty)
			)

		existing_bin_qty, existing_bin_stock_value = capkpi.db.get_value(
			"Bin",
			{"item_code": "_Test Item", "warehouse": "_Test Warehouse - _TC"},
			["actual_qty", "stock_value"],
		)

		pr = make_purchase_receipt()

		stock_value_difference = capkpi.db.get_value(
			"Stock Ledger Entry",
			{
				"voucher_type": "Purchase Receipt",
				"voucher_no": pr.name,
				"item_code": "_Test Item",
				"warehouse": "_Test Warehouse - _TC",
			},
			"stock_value_difference",
		)

		self.assertEqual(stock_value_difference, 250)

		current_bin_stock_value = capkpi.db.get_value(
			"Bin", {"item_code": "_Test Item", "warehouse": "_Test Warehouse - _TC"}, "stock_value"
		)
		self.assertEqual(current_bin_stock_value, existing_bin_stock_value + 250)

		self.assertFalse(get_gl_entries("Purchase Receipt", pr.name))

		pr.cancel()

	def test_batched_serial_no_purchase(self):
		item = capkpi.db.exists("Item", {"item_name": "Batched Serialized Item"})
		if not item:
			item = create_item("Batched Serialized Item")
			item.has_batch_no = 1
			item.create_new_batch = 1
			item.has_serial_no = 1
			item.batch_number_series = "BS-BATCH-.##"
			item.serial_no_series = "BS-.####"
			item.save()
		else:
			item = capkpi.get_doc("Item", {"item_name": "Batched Serialized Item"})

		pr = make_purchase_receipt(item_code=item.name, qty=5, rate=500)

		self.assertTrue(capkpi.db.get_value("Batch", {"item": item.name, "reference_name": pr.name}))

		pr.load_from_db()
		batch_no = pr.items[0].batch_no
		pr.cancel()

		self.assertFalse(capkpi.db.get_value("Batch", {"item": item.name, "reference_name": pr.name}))
		self.assertFalse(capkpi.db.get_all("Serial No", {"batch_no": batch_no}))

	def test_duplicate_serial_nos(self):
		from erp.stock.doctype.delivery_note.test_delivery_note import create_delivery_note

		item = capkpi.db.exists("Item", {"item_name": "Test Serialized Item 123"})
		if not item:
			item = create_item("Test Serialized Item 123")
			item.has_serial_no = 1
			item.serial_no_series = "TSI123-.####"
			item.save()
		else:
			item = capkpi.get_doc("Item", {"item_name": "Test Serialized Item 123"})

		# First make purchase receipt
		pr = make_purchase_receipt(item_code=item.name, qty=2, rate=500)
		pr.load_from_db()

		serial_nos = capkpi.db.get_value(
			"Stock Ledger Entry",
			{"voucher_type": "Purchase Receipt", "voucher_no": pr.name, "item_code": item.name},
			"serial_no",
		)

		serial_nos = get_serial_nos(serial_nos)

		self.assertEquals(get_serial_nos(pr.items[0].serial_no), serial_nos)

		# Then tried to receive same serial nos in difference company
		pr_different_company = make_purchase_receipt(
			item_code=item.name,
			qty=2,
			rate=500,
			serial_no="\n".join(serial_nos),
			company="_Test Company 1",
			do_not_submit=True,
			warehouse="Stores - _TC1",
		)

		self.assertRaises(SerialNoDuplicateError, pr_different_company.submit)

		# Then made delivery note to remove the serial nos from stock
		dn = create_delivery_note(item_code=item.name, qty=2, rate=1500, serial_no="\n".join(serial_nos))
		dn.load_from_db()
		self.assertEquals(get_serial_nos(dn.items[0].serial_no), serial_nos)

		posting_date = add_days(today(), -3)

		# Try to receive same serial nos again in the same company with backdated.
		pr1 = make_purchase_receipt(
			item_code=item.name,
			qty=2,
			rate=500,
			posting_date=posting_date,
			serial_no="\n".join(serial_nos),
			do_not_submit=True,
		)

		self.assertRaises(SerialNoExistsInFutureTransaction, pr1.submit)

		# Try to receive same serial nos with different company with backdated.
		pr2 = make_purchase_receipt(
			item_code=item.name,
			qty=2,
			rate=500,
			posting_date=posting_date,
			serial_no="\n".join(serial_nos),
			company="_Test Company 1",
			do_not_submit=True,
			warehouse="Stores - _TC1",
		)

		self.assertRaises(SerialNoExistsInFutureTransaction, pr2.submit)

		# Receive the same serial nos after the delivery note posting date and time
		make_purchase_receipt(item_code=item.name, qty=2, rate=500, serial_no="\n".join(serial_nos))

		# Raise the error for backdated deliver note entry cancel
		self.assertRaises(SerialNoExistsInFutureTransaction, dn.cancel)

	def test_purchase_receipt_gl_entry(self):
		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
			get_multiple_items=True,
			get_taxes_and_charges=True,
		)

		self.assertEqual(cint(erp.is_perpetual_inventory_enabled(pr.company)), 1)

		gl_entries = get_gl_entries("Purchase Receipt", pr.name)

		self.assertTrue(gl_entries)

		stock_in_hand_account = get_inventory_account(pr.company, pr.items[0].warehouse)
		fixed_asset_account = get_inventory_account(pr.company, pr.items[1].warehouse)

		if stock_in_hand_account == fixed_asset_account:
			expected_values = {
				stock_in_hand_account: [750.0, 0.0],
				"Stock Received But Not Billed - TCP1": [0.0, 500.0],
				"_Test Account Shipping Charges - TCP1": [0.0, 100.0],
				"_Test Account Customs Duty - TCP1": [0.0, 150.0],
			}
		else:
			expected_values = {
				stock_in_hand_account: [375.0, 0.0],
				fixed_asset_account: [375.0, 0.0],
				"Stock Received But Not Billed - TCP1": [0.0, 500.0],
				"_Test Account Shipping Charges - TCP1": [0.0, 250.0],
			}
		for gle in gl_entries:
			self.assertEqual(expected_values[gle.account][0], gle.debit)
			self.assertEqual(expected_values[gle.account][1], gle.credit)

		pr.cancel()
		self.assertTrue(get_gl_entries("Purchase Receipt", pr.name))

	def test_subcontracting(self):
		from erp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry

		capkpi.db.set_value(
			"Buying Settings", None, "backflush_raw_materials_of_subcontract_based_on", "BOM"
		)

		make_stock_entry(
			item_code="_Test Item", qty=100, target="_Test Warehouse 1 - _TC", basic_rate=100
		)
		make_stock_entry(
			item_code="_Test Item Home Desktop 100",
			qty=100,
			target="_Test Warehouse 1 - _TC",
			basic_rate=100,
		)
		pr = make_purchase_receipt(item_code="_Test FG Item", qty=10, rate=500, is_subcontracted="Yes")
		self.assertEqual(len(pr.get("supplied_items")), 2)

		rm_supp_cost = sum(d.amount for d in pr.get("supplied_items"))
		self.assertEqual(pr.get("items")[0].rm_supp_cost, flt(rm_supp_cost, 2))

		pr.cancel()

	def test_subcontracting_gle_fg_item_rate_zero(self):
		from erp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry

		capkpi.db.set_value(
			"Buying Settings", None, "backflush_raw_materials_of_subcontract_based_on", "BOM"
		)

		se1 = make_stock_entry(
			item_code="_Test Item",
			target="Work In Progress - TCP1",
			qty=100,
			basic_rate=100,
			company="_Test Company with perpetual inventory",
		)

		se2 = make_stock_entry(
			item_code="_Test Item Home Desktop 100",
			target="Work In Progress - TCP1",
			qty=100,
			basic_rate=100,
			company="_Test Company with perpetual inventory",
		)

		pr = make_purchase_receipt(
			item_code="_Test FG Item",
			qty=10,
			rate=0,
			is_subcontracted="Yes",
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work In Progress - TCP1",
		)

		gl_entries = get_gl_entries("Purchase Receipt", pr.name)

		self.assertFalse(gl_entries)

		pr.cancel()
		se1.cancel()
		se2.cancel()

	def test_subcontracting_over_receipt(self):
		"""
		Behaviour: Raise multiple PRs against one PO that in total
		        receive more than the required qty in the PO.
		Expected Result: Error Raised for Over Receipt against PO.
		"""
		from erp.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		from erp.buying.doctype.purchase_order.purchase_order import (
			make_rm_stock_entry as make_subcontract_transfer_entry,
		)
		from erp.buying.doctype.purchase_order.test_purchase_order import (
			create_purchase_order,
			make_subcontracted_item,
			update_backflush_based_on,
		)
		from erp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry

		update_backflush_based_on("Material Transferred for Subcontract")
		item_code = "_Test Subcontracted FG Item 1"
		make_subcontracted_item(item_code=item_code)

		po = create_purchase_order(
			item_code=item_code,
			qty=1,
			include_exploded_items=0,
			is_subcontracted="Yes",
			supplier_warehouse="_Test Warehouse 1 - _TC",
		)

		# stock raw materials in a warehouse before transfer
		se1 = make_stock_entry(
			target="_Test Warehouse - _TC", item_code="Test Extra Item 1", qty=10, basic_rate=100
		)
		se2 = make_stock_entry(
			target="_Test Warehouse - _TC", item_code="_Test FG Item", qty=1, basic_rate=100
		)
		se3 = make_stock_entry(
			target="_Test Warehouse - _TC", item_code="Test Extra Item 2", qty=1, basic_rate=100
		)

		rm_items = [
			{
				"item_code": item_code,
				"rm_item_code": po.supplied_items[0].rm_item_code,
				"item_name": "_Test FG Item",
				"qty": po.supplied_items[0].required_qty,
				"warehouse": "_Test Warehouse - _TC",
				"stock_uom": "Nos",
			},
			{
				"item_code": item_code,
				"rm_item_code": po.supplied_items[1].rm_item_code,
				"item_name": "Test Extra Item 1",
				"qty": po.supplied_items[1].required_qty,
				"warehouse": "_Test Warehouse - _TC",
				"stock_uom": "Nos",
			},
		]
		rm_item_string = json.dumps(rm_items)
		se = capkpi.get_doc(make_subcontract_transfer_entry(po.name, rm_item_string))
		se.to_warehouse = "_Test Warehouse 1 - _TC"
		se.save()
		se.submit()

		pr1 = make_purchase_receipt(po.name)
		pr2 = make_purchase_receipt(po.name)

		pr1.submit()
		self.assertRaises(capkpi.ValidationError, pr2.submit)

		pr1.cancel()
		se.cancel()
		se1.cancel()
		se2.cancel()
		se3.cancel()
		po.reload()
		pr2.load_from_db()

		if pr2.docstatus == 1 and capkpi.db.get_value(
			"Stock Ledger Entry", {"voucher_no": pr2.name, "is_cancelled": 0}, "name"
		):
			pr2.cancel()

			po.load_from_db()
			po.cancel()

	def test_serial_no_supplier(self):
		pr = make_purchase_receipt(item_code="_Test Serialized Item With Series", qty=1)
		pr_row_1_serial_no = pr.get("items")[0].serial_no

		self.assertEqual(capkpi.db.get_value("Serial No", pr_row_1_serial_no, "supplier"), pr.supplier)

		pr.cancel()
		self.assertFalse(capkpi.db.get_value("Serial No", pr_row_1_serial_no, "warehouse"))

	def test_rejected_serial_no(self):
		pr = capkpi.copy_doc(test_records[0])
		pr.get("items")[0].item_code = "_Test Serialized Item With Series"
		pr.get("items")[0].qty = 3
		pr.get("items")[0].rejected_qty = 2
		pr.get("items")[0].received_qty = 5
		pr.get("items")[0].rejected_warehouse = "_Test Rejected Warehouse - _TC"
		pr.insert()
		pr.submit()

		accepted_serial_nos = pr.get("items")[0].serial_no.split("\n")
		self.assertEqual(len(accepted_serial_nos), 3)
		for serial_no in accepted_serial_nos:
			self.assertEqual(
				capkpi.db.get_value("Serial No", serial_no, "warehouse"), pr.get("items")[0].warehouse
			)

		rejected_serial_nos = pr.get("items")[0].rejected_serial_no.split("\n")
		self.assertEqual(len(rejected_serial_nos), 2)
		for serial_no in rejected_serial_nos:
			self.assertEqual(
				capkpi.db.get_value("Serial No", serial_no, "warehouse"), pr.get("items")[0].rejected_warehouse
			)

		pr.cancel()

	def test_purchase_return_partial(self):
		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
		)

		return_pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
			is_return=1,
			return_against=pr.name,
			qty=-2,
			do_not_submit=1,
		)
		return_pr.items[0].purchase_receipt_item = pr.items[0].name
		return_pr.submit()

		# check sle
		outgoing_rate = capkpi.db.get_value(
			"Stock Ledger Entry",
			{"voucher_type": "Purchase Receipt", "voucher_no": return_pr.name},
			"outgoing_rate",
		)

		self.assertEqual(outgoing_rate, 50)

		# check gl entries for return
		gl_entries = get_gl_entries("Purchase Receipt", return_pr.name)

		self.assertTrue(gl_entries)
		stock_in_hand_account = get_inventory_account(return_pr.company)

		expected_values = {
			stock_in_hand_account: [0.0, 100.0],
			"Stock Received But Not Billed - TCP1": [100.0, 0.0],
		}

		for gle in gl_entries:
			self.assertEqual(expected_values[gle.account][0], gle.debit)
			self.assertEqual(expected_values[gle.account][1], gle.credit)

		# hack because new_doc isn't considering is_return portion of status_updater
		returned = capkpi.get_doc("Purchase Receipt", return_pr.name)
		returned.update_prevdoc_status()
		pr.load_from_db()

		# Check if Original PR updated
		self.assertEqual(pr.items[0].returned_qty, 2)
		self.assertEqual(pr.per_returned, 40)

		from erp.controllers.sales_and_purchase_return import make_return_doc

		return_pr_2 = make_return_doc("Purchase Receipt", pr.name)

		# Check if unreturned amount is mapped in 2nd return
		self.assertEqual(return_pr_2.items[0].qty, -3)

		# Make PI against unreturned amount
		buying_settings = capkpi.get_single("Buying Settings")
		buying_settings.bill_for_rejected_quantity_in_purchase_invoice = 0
		buying_settings.save()

		pi = make_purchase_invoice(pr.name)
		pi.submit()

		self.assertEqual(pi.items[0].qty, 3)

		buying_settings.bill_for_rejected_quantity_in_purchase_invoice = 1
		buying_settings.save()

		pr.load_from_db()
		# PR should be completed on billing all unreturned amount
		self.assertEqual(pr.items[0].billed_amt, 150)
		self.assertEqual(pr.per_billed, 100)
		self.assertEqual(pr.status, "Completed")

		pi.load_from_db()
		pi.cancel()

		pr.load_from_db()
		self.assertEqual(pr.per_billed, 0)

		return_pr.cancel()
		pr.cancel()

	def test_purchase_return_full(self):
		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
		)

		return_pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
			is_return=1,
			return_against=pr.name,
			qty=-5,
			do_not_submit=1,
		)
		return_pr.items[0].purchase_receipt_item = pr.items[0].name
		return_pr.submit()

		# hack because new_doc isn't considering is_return portion of status_updater
		returned = capkpi.get_doc("Purchase Receipt", return_pr.name)
		returned.update_prevdoc_status()
		pr.load_from_db()

		# Check if Original PR updated
		self.assertEqual(pr.items[0].returned_qty, 5)
		self.assertEqual(pr.per_returned, 100)
		self.assertEqual(pr.status, "Return Issued")

		return_pr.cancel()
		pr.cancel()

	def test_purchase_return_for_rejected_qty(self):
		from erp.stock.doctype.warehouse.test_warehouse import get_warehouse

		rejected_warehouse = "_Test Rejected Warehouse - TCP1"
		if not capkpi.db.exists("Warehouse", rejected_warehouse):
			get_warehouse(
				company="_Test Company with perpetual inventory",
				abbr=" - TCP1",
				warehouse_name="_Test Rejected Warehouse",
			).name

		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
			qty=2,
			rejected_qty=2,
			rejected_warehouse=rejected_warehouse,
		)

		return_pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
			is_return=1,
			return_against=pr.name,
			qty=-2,
			rejected_qty=-2,
			rejected_warehouse=rejected_warehouse,
		)

		actual_qty = capkpi.db.get_value(
			"Stock Ledger Entry",
			{
				"voucher_type": "Purchase Receipt",
				"voucher_no": return_pr.name,
				"warehouse": return_pr.items[0].rejected_warehouse,
			},
			"actual_qty",
		)

		self.assertEqual(actual_qty, -2)

		return_pr.cancel()
		pr.cancel()

	def test_purchase_receipt_for_rejected_gle_without_accepted_warehouse(self):
		from erp.stock.doctype.warehouse.test_warehouse import get_warehouse

		rejected_warehouse = "_Test Rejected Warehouse - TCP1"
		if not capkpi.db.exists("Warehouse", rejected_warehouse):
			get_warehouse(
				company="_Test Company with perpetual inventory",
				abbr=" - TCP1",
				warehouse_name="_Test Rejected Warehouse",
			).name

		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			received_qty=2,
			rejected_qty=2,
			rejected_warehouse=rejected_warehouse,
			do_not_save=True,
		)

		pr.items[0].qty = 0.0
		pr.items[0].warehouse = ""
		pr.submit()

		actual_qty = capkpi.db.get_value(
			"Stock Ledger Entry",
			{
				"voucher_type": "Purchase Receipt",
				"voucher_no": pr.name,
				"warehouse": pr.items[0].rejected_warehouse,
				"is_cancelled": 0,
			},
			"actual_qty",
		)

		self.assertEqual(actual_qty, 2)
		self.assertFalse(pr.items[0].warehouse)
		pr.cancel()

	def test_purchase_return_for_serialized_items(self):
		def _check_serial_no_values(serial_no, field_values):
			serial_no = capkpi.get_doc("Serial No", serial_no)
			for field, value in iteritems(field_values):
				self.assertEqual(cstr(serial_no.get(field)), value)

		from erp.stock.doctype.serial_no.serial_no import get_serial_nos

		pr = make_purchase_receipt(item_code="_Test Serialized Item With Series", qty=1)

		serial_no = get_serial_nos(pr.get("items")[0].serial_no)[0]

		_check_serial_no_values(
			serial_no, {"warehouse": "_Test Warehouse - _TC", "purchase_document_no": pr.name}
		)

		return_pr = make_purchase_receipt(
			item_code="_Test Serialized Item With Series",
			qty=-1,
			is_return=1,
			return_against=pr.name,
			serial_no=serial_no,
		)

		_check_serial_no_values(
			serial_no,
			{"warehouse": "", "purchase_document_no": pr.name, "delivery_document_no": return_pr.name},
		)

		return_pr.cancel()
		pr.reload()
		pr.cancel()

	def test_purchase_return_for_multi_uom(self):
		item_code = "_Test Purchase Return For Multi-UOM"
		if not capkpi.db.exists("Item", item_code):
			item = make_item(item_code, {"stock_uom": "Box"})
			row = item.append("uoms", {"uom": "Unit", "conversion_factor": 0.1})
			row.db_update()

		pr = make_purchase_receipt(item_code=item_code, qty=1, uom="Box", conversion_factor=1.0)
		return_pr = make_purchase_receipt(
			item_code=item_code,
			qty=-10,
			uom="Unit",
			stock_uom="Box",
			conversion_factor=0.1,
			is_return=1,
			return_against=pr.name,
		)

		self.assertEqual(abs(return_pr.items[0].stock_qty), 1.0)

		return_pr.cancel()
		pr.cancel()

	def test_closed_purchase_receipt(self):
		from erp.stock.doctype.purchase_receipt.purchase_receipt import (
			update_purchase_receipt_status,
		)

		pr = make_purchase_receipt()

		update_purchase_receipt_status(pr.name, "Closed")
		self.assertEqual(capkpi.db.get_value("Purchase Receipt", pr.name, "status"), "Closed")

		pr.reload()
		pr.cancel()

	def test_pr_billing_status(self):
		"""Flow:
		1. PO -> PR1 -> PI
		2. PO -> PI
		3. PO -> PR2.
		"""
		from erp.buying.doctype.purchase_order.purchase_order import (
			make_purchase_invoice as make_purchase_invoice_from_po,
		)
		from erp.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		from erp.buying.doctype.purchase_order.test_purchase_order import create_purchase_order

		po = create_purchase_order()

		pr1 = make_purchase_receipt(po.name)
		pr1.posting_date = today()
		pr1.posting_time = "10:00"
		pr1.get("items")[0].received_qty = 2
		pr1.get("items")[0].qty = 2
		pr1.submit()

		pi1 = make_purchase_invoice(pr1.name)
		pi1.submit()

		pr1.load_from_db()
		self.assertEqual(pr1.per_billed, 100)

		pi2 = make_purchase_invoice_from_po(po.name)
		pi2.get("items")[0].qty = 4
		pi2.submit()

		pr2 = make_purchase_receipt(po.name)
		pr2.posting_date = today()
		pr2.posting_time = "08:00"
		pr2.get("items")[0].received_qty = 5
		pr2.get("items")[0].qty = 5
		pr2.submit()

		pr1.load_from_db()
		self.assertEqual(pr1.get("items")[0].billed_amt, 1000)
		self.assertEqual(pr1.per_billed, 100)
		self.assertEqual(pr1.status, "Completed")

		pr2.load_from_db()
		self.assertEqual(pr2.get("items")[0].billed_amt, 2000)
		self.assertEqual(pr2.per_billed, 80)
		self.assertEqual(pr2.status, "To Bill")

		pr2.cancel()
		pi2.reload()
		pi2.cancel()
		pi1.reload()
		pi1.cancel()
		pr1.reload()
		pr1.cancel()
		po.reload()
		po.cancel()

	def test_serial_no_against_purchase_receipt(self):
		from erp.stock.doctype.serial_no.serial_no import get_serial_nos

		item_code = "Test Manual Created Serial No"
		if not capkpi.db.exists("Item", item_code):
			item = make_item(item_code, dict(has_serial_no=1))

		serial_no = "12903812901"
		pr_doc = make_purchase_receipt(item_code=item_code, qty=1, serial_no=serial_no)

		self.assertEqual(
			serial_no,
			capkpi.db.get_value(
				"Serial No",
				{"purchase_document_type": "Purchase Receipt", "purchase_document_no": pr_doc.name},
				"name",
			),
		)

		pr_doc.cancel()

		# check for the auto created serial nos
		item_code = "Test Auto Created Serial No"
		if not capkpi.db.exists("Item", item_code):
			make_item(item_code, dict(has_serial_no=1, serial_no_series="KLJL.###"))

		new_pr_doc = make_purchase_receipt(item_code=item_code, qty=1)

		serial_no = get_serial_nos(new_pr_doc.items[0].serial_no)[0]
		self.assertEqual(
			serial_no,
			capkpi.db.get_value(
				"Serial No",
				{"purchase_document_type": "Purchase Receipt", "purchase_document_no": new_pr_doc.name},
				"name",
			),
		)

		new_pr_doc.cancel()

	def test_auto_asset_creation(self):
		asset_item = "Test Asset Item"

		if not capkpi.db.exists("Item", asset_item):
			asset_category = capkpi.get_all("Asset Category")

			if asset_category:
				asset_category = asset_category[0].name

			if not asset_category:
				doc = capkpi.get_doc(
					{
						"doctype": "Asset Category",
						"asset_category_name": "Test Asset Category",
						"depreciation_method": "Straight Line",
						"total_number_of_depreciations": 12,
						"frequency_of_depreciation": 1,
						"accounts": [
							{
								"company_name": "_Test Company",
								"fixed_asset_account": "_Test Fixed Asset - _TC",
								"accumulated_depreciation_account": "_Test Accumulated Depreciations - _TC",
								"depreciation_expense_account": "_Test Depreciations - _TC",
							}
						],
					}
				).insert()

				asset_category = doc.name

			item_data = make_item(
				asset_item,
				{
					"is_stock_item": 0,
					"stock_uom": "Box",
					"is_fixed_asset": 1,
					"auto_create_assets": 1,
					"asset_category": asset_category,
					"asset_naming_series": "ABC.###",
				},
			)
			asset_item = item_data.item_code

		pr = make_purchase_receipt(item_code=asset_item, qty=3)
		assets = capkpi.db.get_all("Asset", filters={"purchase_receipt": pr.name})

		self.assertEqual(len(assets), 3)

		location = capkpi.db.get_value("Asset", assets[0].name, "location")
		self.assertEqual(location, "Test Location")

		pr.cancel()

	def test_purchase_return_with_submitted_asset(self):
		from erp.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return

		pr = make_purchase_receipt(item_code="Test Asset Item", qty=1)

		asset = capkpi.get_doc("Asset", {"purchase_receipt": pr.name})
		asset.available_for_use_date = capkpi.utils.nowdate()
		asset.gross_purchase_amount = 50.0
		asset.append(
			"finance_books",
			{
				"expected_value_after_useful_life": 10,
				"depreciation_method": "Straight Line",
				"total_number_of_depreciations": 3,
				"frequency_of_depreciation": 1,
			},
		)
		asset.submit()

		pr_return = make_purchase_return(pr.name)
		self.assertRaises(capkpi.exceptions.ValidationError, pr_return.submit)

		asset.load_from_db()
		asset.cancel()

		pr_return.submit()

		pr_return.cancel()
		pr.cancel()

	def test_purchase_receipt_cost_center(self):
		from erp.accounts.doctype.cost_center.test_cost_center import create_cost_center

		cost_center = "_Test Cost Center for BS Account - TCP1"
		create_cost_center(
			cost_center_name="_Test Cost Center for BS Account",
			company="_Test Company with perpetual inventory",
		)

		if not capkpi.db.exists("Location", "Test Location"):
			capkpi.get_doc({"doctype": "Location", "location_name": "Test Location"}).insert()

		pr = make_purchase_receipt(
			cost_center=cost_center,
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
		)

		stock_in_hand_account = get_inventory_account(pr.company, pr.get("items")[0].warehouse)
		gl_entries = get_gl_entries("Purchase Receipt", pr.name)

		self.assertTrue(gl_entries)

		expected_values = {
			"Stock Received But Not Billed - TCP1": {"cost_center": cost_center},
			stock_in_hand_account: {"cost_center": cost_center},
		}
		for i, gle in enumerate(gl_entries):
			self.assertEqual(expected_values[gle.account]["cost_center"], gle.cost_center)

		pr.cancel()

	def test_purchase_receipt_cost_center_with_balance_sheet_account(self):
		if not capkpi.db.exists("Location", "Test Location"):
			capkpi.get_doc({"doctype": "Location", "location_name": "Test Location"}).insert()

		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory",
			warehouse="Stores - TCP1",
			supplier_warehouse="Work in Progress - TCP1",
		)

		stock_in_hand_account = get_inventory_account(pr.company, pr.get("items")[0].warehouse)
		gl_entries = get_gl_entries("Purchase Receipt", pr.name)

		self.assertTrue(gl_entries)
		cost_center = pr.get("items")[0].cost_center

		expected_values = {
			"Stock Received But Not Billed - TCP1": {"cost_center": cost_center},
			stock_in_hand_account: {"cost_center": cost_center},
		}
		for i, gle in enumerate(gl_entries):
			self.assertEqual(expected_values[gle.account]["cost_center"], gle.cost_center)

		pr.cancel()

	def test_make_purchase_invoice_from_pr_for_returned_qty(self):
		from erp.buying.doctype.purchase_order.test_purchase_order import (
			create_pr_against_po,
			create_purchase_order,
		)

		po = create_purchase_order()
		pr = create_pr_against_po(po.name)

		pr1 = make_purchase_receipt(qty=-1, is_return=1, return_against=pr.name, do_not_submit=True)
		pr1.items[0].purchase_order = po.name
		pr1.items[0].purchase_order_item = po.items[0].name
		pr1.items[0].purchase_receipt_item = pr.items[0].name
		pr1.submit()

		pi = make_purchase_invoice(pr.name)
		self.assertEqual(pi.items[0].qty, 3)

		pr1.cancel()
		pr.reload()
		pr.cancel()
		po.reload()
		po.cancel()

	def test_make_purchase_invoice_from_pr_with_returned_qty_duplicate_items(self):
		pr1 = make_purchase_receipt(qty=8, do_not_submit=True)
		pr1.append(
			"items",
			{
				"item_code": "_Test Item",
				"warehouse": "_Test Warehouse - _TC",
				"qty": 1,
				"received_qty": 1,
				"rate": 100,
				"conversion_factor": 1.0,
			},
		)
		pr1.submit()

		pi1 = make_purchase_invoice(pr1.name)
		pi1.items[0].qty = 4
		pi1.items.pop(1)
		pi1.save()
		pi1.submit()

		pr2 = make_purchase_receipt(qty=-2, is_return=1, return_against=pr1.name, do_not_submit=True)
		pr2.items[0].purchase_receipt_item = pr1.items[0].name
		pr2.submit()

		pi2 = make_purchase_invoice(pr1.name)
		self.assertEqual(pi2.items[0].qty, 2)
		self.assertEqual(pi2.items[1].qty, 1)

		pr2.cancel()
		pi1.cancel()
		pr1.reload()
		pr1.cancel()

	def test_stock_transfer_from_purchase_receipt(self):
		pr1 = make_purchase_receipt(
			warehouse="Work In Progress - TCP1", company="_Test Company with perpetual inventory"
		)

		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory", warehouse="Stores - TCP1", do_not_save=1
		)

		pr.supplier_warehouse = ""
		pr.items[0].from_warehouse = "Work In Progress - TCP1"

		pr.submit()

		gl_entries = get_gl_entries("Purchase Receipt", pr.name)
		sl_entries = get_sl_entries("Purchase Receipt", pr.name)

		self.assertFalse(gl_entries)

		expected_sle = {"Work In Progress - TCP1": -5, "Stores - TCP1": 5}

		for sle in sl_entries:
			self.assertEqual(expected_sle[sle.warehouse], sle.actual_qty)

		pr.cancel()
		pr1.cancel()

	def test_stock_transfer_from_purchase_receipt_with_valuation(self):
		create_warehouse(
			"_Test Warehouse for Valuation",
			company="_Test Company with perpetual inventory",
			properties={"account": "_Test Account Stock In Hand - TCP1"},
		)

		pr1 = make_purchase_receipt(
			warehouse="_Test Warehouse for Valuation - TCP1",
			company="_Test Company with perpetual inventory",
		)

		pr = make_purchase_receipt(
			company="_Test Company with perpetual inventory", warehouse="Stores - TCP1", do_not_save=1
		)

		pr.items[0].from_warehouse = "_Test Warehouse for Valuation - TCP1"
		pr.supplier_warehouse = ""

		pr.append(
			"taxes",
			{
				"charge_type": "On Net Total",
				"account_head": "_Test Account Shipping Charges - TCP1",
				"category": "Valuation and Total",
				"cost_center": "Main - TCP1",
				"description": "Test",
				"rate": 9,
			},
		)

		pr.submit()

		gl_entries = get_gl_entries("Purchase Receipt", pr.name)
		sl_entries = get_sl_entries("Purchase Receipt", pr.name)

		expected_gle = [
			["Stock In Hand - TCP1", 272.5, 0.0],
			["_Test Account Stock In Hand - TCP1", 0.0, 250.0],
			["_Test Account Shipping Charges - TCP1", 0.0, 22.5],
		]

		expected_sle = {"_Test Warehouse for Valuation - TCP1": -5, "Stores - TCP1": 5}

		for sle in sl_entries:
			self.assertEqual(expected_sle[sle.warehouse], sle.actual_qty)

		for i, gle in enumerate(gl_entries):
			self.assertEqual(gle.account, expected_gle[i][0])
			self.assertEqual(gle.debit, expected_gle[i][1])
			self.assertEqual(gle.credit, expected_gle[i][2])

		pr.cancel()
		pr1.cancel()

	def test_subcontracted_pr_for_multi_transfer_batches(self):
		from erp.buying.doctype.purchase_order.purchase_order import (
			make_purchase_receipt,
			make_rm_stock_entry,
		)
		from erp.buying.doctype.purchase_order.test_purchase_order import (
			create_purchase_order,
			update_backflush_based_on,
		)
		from erp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry

		update_backflush_based_on("Material Transferred for Subcontract")
		item_code = "_Test Subcontracted FG Item 3"

		make_item(
			"Sub Contracted Raw Material 3",
			{"is_stock_item": 1, "is_sub_contracted_item": 1, "has_batch_no": 1, "create_new_batch": 1},
		)

		create_subcontracted_item(
			item_code=item_code, has_batch_no=1, raw_materials=["Sub Contracted Raw Material 3"]
		)

		order_qty = 500
		po = create_purchase_order(
			item_code=item_code,
			qty=order_qty,
			is_subcontracted="Yes",
			supplier_warehouse="_Test Warehouse 1 - _TC",
		)

		ste1 = make_stock_entry(
			target="_Test Warehouse - _TC",
			item_code="Sub Contracted Raw Material 3",
			qty=300,
			basic_rate=100,
		)
		ste2 = make_stock_entry(
			target="_Test Warehouse - _TC",
			item_code="Sub Contracted Raw Material 3",
			qty=200,
			basic_rate=100,
		)

		transferred_batch = {ste1.items[0].batch_no: 300, ste2.items[0].batch_no: 200}

		rm_items = [
			{
				"item_code": item_code,
				"rm_item_code": "Sub Contracted Raw Material 3",
				"item_name": "_Test Item",
				"qty": 300,
				"warehouse": "_Test Warehouse - _TC",
				"stock_uom": "Nos",
				"name": po.supplied_items[0].name,
			},
			{
				"item_code": item_code,
				"rm_item_code": "Sub Contracted Raw Material 3",
				"item_name": "_Test Item",
				"qty": 200,
				"warehouse": "_Test Warehouse - _TC",
				"stock_uom": "Nos",
				"name": po.supplied_items[0].name,
			},
		]

		rm_item_string = json.dumps(rm_items)
		se = capkpi.get_doc(make_rm_stock_entry(po.name, rm_item_string))
		self.assertEqual(len(se.items), 2)
		se.items[0].batch_no = ste1.items[0].batch_no
		se.items[1].batch_no = ste2.items[0].batch_no
		se.submit()

		supplied_qty = capkpi.db.get_value(
			"Purchase Order Item Supplied",
			{"parent": po.name, "rm_item_code": "Sub Contracted Raw Material 3"},
			"supplied_qty",
		)

		self.assertEqual(supplied_qty, 500.00)

		pr = make_purchase_receipt(po.name)
		pr.save()
		self.assertEqual(len(pr.supplied_items), 2)

		for row in pr.supplied_items:
			self.assertEqual(transferred_batch.get(row.batch_no), row.consumed_qty)

		update_backflush_based_on("BOM")

		pr.delete()
		se.cancel()
		ste2.cancel()
		ste1.cancel()
		po.cancel()

	def test_po_to_pi_and_po_to_pr_worflow_full(self):
		"""Test following behaviour:
		- Create PO
		- Create PI from PO and submit
		- Create PR from PO and submit
		"""
		from erp.buying.doctype.purchase_order import purchase_order, test_purchase_order

		po = test_purchase_order.create_purchase_order()

		pi = purchase_order.make_purchase_invoice(po.name)
		pi.submit()

		pr = purchase_order.make_purchase_receipt(po.name)
		pr.submit()

		pr.load_from_db()

		self.assertEqual(pr.status, "Completed")
		self.assertEqual(pr.per_billed, 100)

	def test_po_to_pi_and_po_to_pr_worflow_partial(self):
		"""Test following behaviour:
		- Create PO
		- Create partial PI from PO and submit
		- Create PR from PO and submit
		"""
		from erp.buying.doctype.purchase_order import purchase_order, test_purchase_order

		po = test_purchase_order.create_purchase_order()

		pi = purchase_order.make_purchase_invoice(po.name)
		pi.items[0].qty /= 2  # roughly 50%, ^ this function only creates PI with 1 item.
		pi.submit()

		pr = purchase_order.make_purchase_receipt(po.name)
		pr.save()
		# per_billed is only updated after submission.
		self.assertEqual(flt(pr.per_billed), 0)

		pr.submit()

		pi.load_from_db()
		pr.load_from_db()

		self.assertEqual(pr.status, "To Bill")
		self.assertAlmostEqual(pr.per_billed, 50.0, places=2)

	def test_payment_terms_are_fetched_when_creating_purchase_invoice(self):
		from erp.accounts.doctype.payment_entry.test_payment_entry import (
			create_payment_terms_template,
		)
		from erp.accounts.doctype.purchase_invoice.test_purchase_invoice import make_purchase_invoice
		from erp.buying.doctype.purchase_order.test_purchase_order import (
			create_purchase_order,
			make_pr_against_po,
		)
		from erp.selling.doctype.sales_order.test_sales_order import (
			automatically_fetch_payment_terms,
			compare_payment_schedules,
		)

		automatically_fetch_payment_terms()

		po = create_purchase_order(qty=10, rate=100, do_not_save=1)
		create_payment_terms_template()
		po.payment_terms_template = "Test Receivable Template"
		po.submit()

		pr = make_pr_against_po(po.name, received_qty=10)

		pi = make_purchase_invoice(qty=10, rate=100, do_not_save=1)
		pi.items[0].purchase_receipt = pr.name
		pi.items[0].pr_detail = pr.items[0].name
		pi.items[0].purchase_order = po.name
		pi.items[0].po_detail = po.items[0].name
		pi.insert()

		# self.assertEqual(po.payment_terms_template, pi.payment_terms_template)
		compare_payment_schedules(self, po, pi)

		automatically_fetch_payment_terms(enable=0)

	@change_settings("Stock Settings", {"allow_negative_stock": 1})
	def test_neg_to_positive(self):
		from erp.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry

		item_code = "_TestNegToPosItem"
		warehouse = "Stores - TCP1"
		company = "_Test Company with perpetual inventory"
		account = "Stock Received But Not Billed - TCP1"

		make_item(item_code)
		se = make_stock_entry(
			item_code=item_code, from_warehouse=warehouse, qty=50, do_not_save=True, rate=0
		)
		se.items[0].allow_zero_valuation_rate = 1
		se.save()
		se.submit()

		pr = make_purchase_receipt(
			qty=50,
			rate=1,
			item_code=item_code,
			warehouse=warehouse,
			get_taxes_and_charges=True,
			company=company,
		)
		gles = get_gl_entries(pr.doctype, pr.name)

		for gle in gles:
			if gle.account == account:
				self.assertEqual(gle.credit, 50)

	def test_backdated_transaction_for_internal_transfer(self):
		from erp.stock.doctype.delivery_note.delivery_note import make_inter_company_purchase_receipt
		from erp.stock.doctype.delivery_note.test_delivery_note import create_delivery_note

		prepare_data_for_internal_transfer()
		customer = "_Test Internal Customer 2"
		company = "_Test Company with perpetual inventory"

		from_warehouse = create_warehouse("_Test Internal From Warehouse New", company=company)
		to_warehouse = create_warehouse("_Test Internal To Warehouse New", company=company)
		item_doc = create_item("Test Internal Transfer Item")

		target_warehouse = create_warehouse("_Test Internal GIT Warehouse New", company=company)

		make_purchase_receipt(
			item_code=item_doc.name,
			company=company,
			posting_date=add_days(today(), -1),
			warehouse=from_warehouse,
			qty=1,
			rate=100,
		)

		dn1 = create_delivery_note(
			item_code=item_doc.name,
			company=company,
			customer=customer,
			cost_center="Main - TCP1",
			expense_account="Cost of Goods Sold - TCP1",
			qty=1,
			rate=500,
			warehouse=from_warehouse,
			target_warehouse=target_warehouse,
		)

		self.assertEqual(dn1.items[0].rate, 100)

		pr1 = make_inter_company_purchase_receipt(dn1.name)
		pr1.items[0].warehouse = to_warehouse
		self.assertEqual(pr1.items[0].rate, 100)
		pr1.submit()

		# Backdated purchase receipt entry, the valuation rate should be updated for DN1 and PR1
		make_purchase_receipt(
			item_code=item_doc.name,
			company=company,
			posting_date=add_days(today(), -2),
			warehouse=from_warehouse,
			qty=1,
			rate=200,
		)

		dn_value = capkpi.db.get_value(
			"Stock Ledger Entry",
			{"voucher_type": "Delivery Note", "voucher_no": dn1.name, "warehouse": target_warehouse},
			"stock_value_difference",
		)

		self.assertEqual(abs(dn_value), 200.00)

		pr_value = capkpi.db.get_value(
			"Stock Ledger Entry",
			{"voucher_type": "Purchase Receipt", "voucher_no": pr1.name, "warehouse": to_warehouse},
			"stock_value_difference",
		)

		self.assertEqual(abs(pr_value), 200.00)
		pr1.load_from_db()

		self.assertEqual(pr1.items[0].valuation_rate, 200)
		self.assertEqual(pr1.items[0].rate, 100)

		Gl = capkpi.qb.DocType("GL Entry")

		query = (
			capkpi.qb.from_(Gl)
			.select(
				(fn.Sum(Gl.debit) - fn.Sum(Gl.credit)).as_("value"),
			)
			.where((Gl.voucher_type == pr1.doctype) & (Gl.voucher_no == pr1.name))
		).run(as_dict=True)

		self.assertEqual(query[0].value, 0)

	def test_batch_expiry_for_purchase_receipt(self):
		from erp.controllers.sales_and_purchase_return import make_return_doc

		item = make_item(
			"_Test Batch Item For Return Check",
			{
				"is_purchase_item": 1,
				"is_stock_item": 1,
				"has_batch_no": 1,
				"create_new_batch": 1,
				"batch_number_series": "TBIRC.#####",
			},
		)

		pi = make_purchase_receipt(
			qty=1,
			item_code=item.name,
			update_stock=True,
		)

		pi.load_from_db()
		batch_no = pi.items[0].batch_no
		self.assertTrue(batch_no)

		capkpi.db.set_value("Batch", batch_no, "expiry_date", add_days(today(), -1))

		return_pi = make_return_doc(pi.doctype, pi.name)
		return_pi.save().submit()

		self.assertTrue(return_pi.docstatus == 1)


def prepare_data_for_internal_transfer():
	from erp.accounts.doctype.sales_invoice.test_sales_invoice import create_internal_supplier
	from erp.selling.doctype.customer.test_customer import create_internal_customer

	company = "_Test Company with perpetual inventory"

	create_internal_customer(
		"_Test Internal Customer 2",
		company,
		company,
	)

	create_internal_supplier(
		"_Test Internal Supplier 2",
		company,
		company,
	)

	if not capkpi.db.get_value("Company", company, "unrealized_profit_loss_account"):
		account = "Unrealized Profit and Loss - TCP1"
		if not capkpi.db.exists("Account", account):
			capkpi.get_doc(
				{
					"doctype": "Account",
					"account_name": "Unrealized Profit and Loss",
					"parent_account": "Direct Income - TCP1",
					"company": company,
					"is_group": 0,
					"account_type": "Income Account",
				}
			).insert()

		capkpi.db.set_value("Company", company, "unrealized_profit_loss_account", account)


def get_sl_entries(voucher_type, voucher_no):
	return capkpi.db.sql(
		""" select actual_qty, warehouse, stock_value_difference
		from `tabStock Ledger Entry` where voucher_type=%s and voucher_no=%s
		order by posting_time desc""",
		(voucher_type, voucher_no),
		as_dict=1,
	)


def get_gl_entries(voucher_type, voucher_no):
	return capkpi.db.sql(
		"""select account, debit, credit, cost_center, is_cancelled
		from `tabGL Entry` where voucher_type=%s and voucher_no=%s
		order by account desc""",
		(voucher_type, voucher_no),
		as_dict=1,
	)


def get_taxes(**args):

	args = capkpi._dict(args)

	return [
		{
			"account_head": "_Test Account Shipping Charges - TCP1",
			"add_deduct_tax": "Add",
			"category": "Valuation and Total",
			"charge_type": "Actual",
			"cost_center": args.cost_center or "Main - TCP1",
			"description": "Shipping Charges",
			"doctype": "Purchase Taxes and Charges",
			"parentfield": "taxes",
			"rate": 100.0,
			"tax_amount": 100.0,
		},
		{
			"account_head": "_Test Account VAT - TCP1",
			"add_deduct_tax": "Add",
			"category": "Total",
			"charge_type": "Actual",
			"cost_center": args.cost_center or "Main - TCP1",
			"description": "VAT",
			"doctype": "Purchase Taxes and Charges",
			"parentfield": "taxes",
			"rate": 120.0,
			"tax_amount": 120.0,
		},
		{
			"account_head": "_Test Account Customs Duty - TCP1",
			"add_deduct_tax": "Add",
			"category": "Valuation",
			"charge_type": "Actual",
			"cost_center": args.cost_center or "Main - TCP1",
			"description": "Customs Duty",
			"doctype": "Purchase Taxes and Charges",
			"parentfield": "taxes",
			"rate": 150.0,
			"tax_amount": 150.0,
		},
	]


def get_items(**args):
	args = capkpi._dict(args)
	return [
		{
			"base_amount": 250.0,
			"conversion_factor": 1.0,
			"description": "_Test Item",
			"doctype": "Purchase Receipt Item",
			"item_code": "_Test Item",
			"item_name": "_Test Item",
			"parentfield": "items",
			"qty": 5.0,
			"rate": 50.0,
			"received_qty": 5.0,
			"rejected_qty": 0.0,
			"stock_uom": "_Test UOM",
			"uom": "_Test UOM",
			"warehouse": args.warehouse or "_Test Warehouse - _TC",
			"cost_center": args.cost_center or "Main - _TC",
		},
		{
			"base_amount": 250.0,
			"conversion_factor": 1.0,
			"description": "_Test Item Home Desktop 100",
			"doctype": "Purchase Receipt Item",
			"item_code": "_Test Item Home Desktop 100",
			"item_name": "_Test Item Home Desktop 100",
			"parentfield": "items",
			"qty": 5.0,
			"rate": 50.0,
			"received_qty": 5.0,
			"rejected_qty": 0.0,
			"stock_uom": "_Test UOM",
			"uom": "_Test UOM",
			"warehouse": args.warehouse or "_Test Warehouse 1 - _TC",
			"cost_center": args.cost_center or "Main - _TC",
		},
	]


def make_purchase_receipt(**args):
	if not capkpi.db.exists("Location", "Test Location"):
		capkpi.get_doc({"doctype": "Location", "location_name": "Test Location"}).insert()

	capkpi.db.set_value("Buying Settings", None, "allow_multiple_items", 1)
	pr = capkpi.new_doc("Purchase Receipt")
	args = capkpi._dict(args)
	pr.posting_date = args.posting_date or today()
	if args.posting_time:
		pr.posting_time = args.posting_time
	if args.posting_date or args.posting_time:
		pr.set_posting_time = 1
	pr.company = args.company or "_Test Company"
	pr.supplier = args.supplier or "_Test Supplier"
	pr.is_subcontracted = args.is_subcontracted or "No"
	pr.supplier_warehouse = args.supplier_warehouse or "_Test Warehouse 1 - _TC"
	pr.currency = args.currency or "INR"
	pr.is_return = args.is_return
	pr.return_against = args.return_against
	pr.apply_putaway_rule = args.apply_putaway_rule
	qty = args.qty or 5
	rejected_qty = args.rejected_qty or 0
	received_qty = args.received_qty or flt(rejected_qty) + flt(qty)

	item_code = args.item or args.item_code or "_Test Item"
	uom = args.uom or capkpi.db.get_value("Item", item_code, "stock_uom") or "_Test UOM"
	pr.append(
		"items",
		{
			"item_code": item_code,
			"warehouse": args.warehouse or "_Test Warehouse - _TC",
			"qty": qty,
			"received_qty": received_qty,
			"rejected_qty": rejected_qty,
			"rejected_warehouse": args.rejected_warehouse or "_Test Rejected Warehouse - _TC"
			if rejected_qty != 0
			else "",
			"rate": args.rate if args.rate != None else 50,
			"conversion_factor": args.conversion_factor or 1.0,
			"stock_qty": flt(qty) * (flt(args.conversion_factor) or 1.0),
			"serial_no": args.serial_no,
			"batch_no": args.batch_no,
			"stock_uom": args.stock_uom or "_Test UOM",
			"uom": uom,
			"cost_center": args.cost_center
			or capkpi.get_cached_value("Company", pr.company, "cost_center"),
			"asset_location": args.location or "Test Location",
		},
	)

	if args.get_multiple_items:
		pr.items = []

		company_cost_center = capkpi.get_cached_value("Company", pr.company, "cost_center")
		cost_center = args.cost_center or company_cost_center

		for item in get_items(warehouse=args.warehouse, cost_center=cost_center):
			pr.append("items", item)

	if args.get_taxes_and_charges:
		for tax in get_taxes():
			pr.append("taxes", tax)

	if not args.do_not_save:
		pr.insert()
		if not args.do_not_submit:
			pr.submit()
	return pr


def create_subcontracted_item(**args):
	from erp.manufacturing.doctype.production_plan.test_production_plan import make_bom

	args = capkpi._dict(args)

	if not capkpi.db.exists("Item", args.item_code):
		make_item(
			args.item_code,
			{
				"is_stock_item": 1,
				"is_sub_contracted_item": 1,
				"has_batch_no": args.get("has_batch_no") or 0,
			},
		)

	if not args.raw_materials:
		if not capkpi.db.exists("Item", "Test Extra Item 1"):
			make_item(
				"Test Extra Item 1",
				{
					"is_stock_item": 1,
				},
			)

		if not capkpi.db.exists("Item", "Test Extra Item 2"):
			make_item(
				"Test Extra Item 2",
				{
					"is_stock_item": 1,
				},
			)

		args.raw_materials = ["_Test FG Item", "Test Extra Item 1"]

	if not capkpi.db.get_value("BOM", {"item": args.item_code}, "name"):
		make_bom(item=args.item_code, raw_materials=args.get("raw_materials"))


test_dependencies = ["BOM", "Item Price", "Location"]
test_records = capkpi.get_test_records("Purchase Receipt")