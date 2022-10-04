# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and Contributors
# See license.txt


import capkpi

test_records = capkpi.get_test_records("Item Attribute")

from capkpi.tests.utils import CapKPITestCase

from erp.stock.doctype.item_attribute.item_attribute import ItemAttributeIncrementError


class TestItemAttribute(CapKPITestCase):
	def setUp(self):
		super().setUp()
		if capkpi.db.exists("Item Attribute", "_Test_Length"):
			capkpi.delete_doc("Item Attribute", "_Test_Length")

	def test_numeric_item_attribute(self):
		item_attribute = capkpi.get_doc(
			{
				"doctype": "Item Attribute",
				"attribute_name": "_Test_Length",
				"numeric_values": 1,
				"from_range": 0.0,
				"to_range": 100.0,
				"increment": 0,
			}
		)

		self.assertRaises(ItemAttributeIncrementError, item_attribute.save)

		item_attribute.increment = 0.5
		item_attribute.save()
