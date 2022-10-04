# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.tests.utils import CapKPITestCase
from capkpi.utils import add_days, nowdate

from erp.hr.doctype.employee.test_employee import make_employee
from erp.hr.doctype.shift_assignment.shift_assignment import get_events

test_dependencies = ["Shift Type"]


class TestShiftAssignment(CapKPITestCase):
	def setUp(self):
		capkpi.db.delete("Shift Assignment")
		if not capkpi.db.exists("Shift Type", "Day Shift"):
			capkpi.get_doc(
				{"doctype": "Shift Type", "name": "Day Shift", "start_time": "9:00:00", "end_time": "18:00:00"}
			).insert()

	def test_make_shift_assignment(self):
		shift_assignment = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": "_T-Employee-00001",
				"start_date": nowdate(),
			}
		).insert()
		shift_assignment.submit()

		self.assertEqual(shift_assignment.docstatus, 1)

	def test_overlapping_for_ongoing_shift(self):
		# shift should be Ongoing if Only start_date is present and status = Active

		shift_assignment_1 = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": "_T-Employee-00001",
				"start_date": nowdate(),
				"status": "Active",
			}
		).insert()
		shift_assignment_1.submit()

		self.assertEqual(shift_assignment_1.docstatus, 1)

		shift_assignment = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": "_T-Employee-00001",
				"start_date": add_days(nowdate(), 2),
			}
		)

		self.assertRaises(capkpi.ValidationError, shift_assignment.save)

	def test_overlapping_for_fixed_period_shift(self):
		# shift should is for Fixed period if Only start_date and end_date both are present and status = Active

		shift_assignment_1 = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": "_T-Employee-00001",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 30),
				"status": "Active",
			}
		).insert()
		shift_assignment_1.submit()

		# it should not allowed within period of any shift.
		shift_assignment_3 = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": "_T-Employee-00001",
				"start_date": add_days(nowdate(), 10),
				"end_date": add_days(nowdate(), 35),
				"status": "Active",
			}
		)

		self.assertRaises(capkpi.ValidationError, shift_assignment_3.save)

	def test_shift_assignment_calendar(self):
		employee1 = make_employee("test_shift_assignment1@example.com", company="_Test Company")
		employee2 = make_employee("test_shift_assignment2@example.com", company="_Test Company")
		date = nowdate()

		shift_1 = capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": employee1,
				"start_date": date,
				"status": "Active",
			}
		).submit()

		capkpi.get_doc(
			{
				"doctype": "Shift Assignment",
				"shift_type": "Day Shift",
				"company": "_Test Company",
				"employee": employee2,
				"start_date": date,
				"status": "Active",
			}
		).submit()

		events = get_events(
			start=date, end=date, filters=[["Shift Assignment", "employee", "=", employee1, False]]
		)
		self.assertEqual(len(events), 1)
		self.assertEqual(events[0]["name"], shift_1.name)
