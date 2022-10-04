# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import unittest

import capkpi
from capkpi.utils import getdate

from erp.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates


class TestLeaveBlockList(unittest.TestCase):
	def tearDown(self):
		capkpi.set_user("Administrator")

	def test_get_applicable_block_dates(self):
		capkpi.set_user("test@example.com")
		capkpi.db.set_value(
			"Department", "_Test Department - _TC", "leave_block_list", "_Test Leave Block List"
		)
		self.assertTrue(
			getdate("2013-01-02")
			in [d.block_date for d in get_applicable_block_dates("2013-01-01", "2013-01-03")]
		)

	def test_get_applicable_block_dates_for_allowed_user(self):
		capkpi.set_user("test1@example.com")
		capkpi.db.set_value(
			"Department", "_Test Department 1 - _TC", "leave_block_list", "_Test Leave Block List"
		)
		self.assertEqual(
			[], [d.block_date for d in get_applicable_block_dates("2013-01-01", "2013-01-03")]
		)

	def test_get_applicable_block_dates_all_lists(self):
		capkpi.set_user("test1@example.com")
		capkpi.db.set_value(
			"Department", "_Test Department 1 - _TC", "leave_block_list", "_Test Leave Block List"
		)
		self.assertTrue(
			getdate("2013-01-02")
			in [
				d.block_date for d in get_applicable_block_dates("2013-01-01", "2013-01-03", all_lists=True)
			]
		)


test_dependencies = ["Employee"]

test_records = capkpi.get_test_records("Leave Block List")
