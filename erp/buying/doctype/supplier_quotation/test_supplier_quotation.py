# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.tests.utils import CapKPITestCase


class TestPurchaseOrder(CapKPITestCase):
	def test_make_purchase_order(self):
		from erp.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order

		sq = capkpi.copy_doc(test_records[0]).insert()

		self.assertRaises(capkpi.ValidationError, make_purchase_order, sq.name)

		sq = capkpi.get_doc("Supplier Quotation", sq.name)
		sq.submit()
		po = make_purchase_order(sq.name)

		self.assertEqual(po.doctype, "Purchase Order")
		self.assertEqual(len(po.get("items")), len(sq.get("items")))

		po.naming_series = "_T-Purchase Order-"

		for doc in po.get("items"):
			if doc.get("item_code"):
				doc.set("schedule_date", "2013-04-12")

		po.insert()


test_records = capkpi.get_test_records("Supplier Quotation")
