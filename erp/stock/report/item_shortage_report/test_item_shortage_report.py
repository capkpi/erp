# Copyright (c) 2022, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import capkpi
from capkpi.tests.utils import CapKPITestCase

from erp.selling.doctype.sales_order.test_sales_order import make_sales_order
from erp.stock.doctype.item.test_item import make_item
from erp.stock.report.item_shortage_report.item_shortage_report import (
	execute as item_shortage_report,
)


class TestItemShortageReport(CapKPITestCase):
	def test_item_shortage_report(self):
		item = make_item().name
		so = make_sales_order(item_code=item)

		reserved_qty, projected_qty = capkpi.db.get_value(
			"Bin",
			{
				"item_code": item,
				"warehouse": so.items[0].warehouse,
			},
			["reserved_qty", "projected_qty"],
		)
		self.assertEqual(reserved_qty, so.items[0].qty)
		self.assertEqual(projected_qty, -(so.items[0].qty))

		filters = {
			"company": so.company,
		}
		report_data = item_shortage_report(filters)[1]
		item_code_list = [row.get("item_code") for row in report_data]
		self.assertIn(item, item_code_list)

		filters = {
			"company": so.company,
			"warehouse": [so.items[0].warehouse],
		}
		report_data = item_shortage_report(filters)[1]
		item_code_list = [row.get("item_code") for row in report_data]
		self.assertIn(item, item_code_list)

		filters = {
			"company": so.company,
			"warehouse": ["Work In Progress - _TC"],
		}
		report_data = item_shortage_report(filters)[1]
		item_code_list = [row.get("item_code") for row in report_data]
		self.assertNotIn(item, item_code_list)
