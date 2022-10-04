# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

test_dependencies = ["Employee Onboarding"]


class TestEmployeeSeparation(unittest.TestCase):
	def test_employee_separation(self):
		employee = capkpi.db.get_value("Employee", {"status": "Active"})
		separation = capkpi.new_doc("Employee Separation")
		separation.employee = employee
		separation.company = "_Test Company"
		separation.append("activities", {"activity_name": "Deactivate Employee", "role": "HR User"})
		separation.boarding_status = "Pending"
		separation.insert()
		separation.submit()
		self.assertEqual(separation.docstatus, 1)
		separation.cancel()
		self.assertEqual(separation.project, "")
