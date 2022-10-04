# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and Contributors
# See license.txt

import unittest

import capkpi

from erp.projects.doctype.activity_cost.activity_cost import DuplicationError


class TestActivityCost(unittest.TestCase):
	def test_duplication(self):
		capkpi.db.sql("delete from `tabActivity Cost`")
		activity_cost1 = capkpi.new_doc("Activity Cost")
		activity_cost1.update(
			{
				"employee": "_T-Employee-00001",
				"employee_name": "_Test Employee",
				"activity_type": "_Test Activity Type 1",
				"billing_rate": 100,
				"costing_rate": 50,
			}
		)
		activity_cost1.insert()
		activity_cost2 = capkpi.copy_doc(activity_cost1)
		self.assertRaises(DuplicationError, activity_cost2.insert)
		capkpi.db.sql("delete from `tabActivity Cost`")
