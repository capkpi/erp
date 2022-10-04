# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestIssuePriority(unittest.TestCase):
	def test_priorities(self):
		make_priorities()
		priorities = capkpi.get_list("Issue Priority")

		for priority in priorities:
			self.assertIn(priority.name, ["Low", "Medium", "High"])


def make_priorities():
	insert_priority("Low")
	insert_priority("Medium")
	insert_priority("High")


def insert_priority(name):
	if not capkpi.db.exists("Issue Priority", name):
		capkpi.get_doc({"doctype": "Issue Priority", "name": name}).insert(ignore_permissions=True)
