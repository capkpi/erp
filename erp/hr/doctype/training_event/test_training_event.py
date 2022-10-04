# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import add_days, today

from erp.payroll.doctype.salary_structure.test_salary_structure import make_employee


class TestTrainingEvent(unittest.TestCase):
	def setUp(self):
		create_training_program("Basic Training")
		employee = make_employee("robert_loan@trainig.com")
		employee2 = make_employee("suzie.tan@trainig.com")
		self.attendees = [{"employee": employee}, {"employee": employee2}]

	def test_training_event_status_update(self):
		training_event = create_training_event(self.attendees)
		training_event.submit()

		training_event.event_status = "Completed"
		training_event.save()
		training_event.reload()

		for entry in training_event.employees:
			self.assertEqual(entry.status, "Completed")

		training_event.event_status = "Scheduled"
		training_event.save()
		training_event.reload()

		for entry in training_event.employees:
			self.assertEqual(entry.status, "Open")

	def tearDown(self):
		capkpi.db.rollback()


def create_training_program(training_program):
	if not capkpi.db.get_value("Training Program", training_program):
		capkpi.get_doc(
			{
				"doctype": "Training Program",
				"training_program": training_program,
				"description": training_program,
			}
		).insert()


def create_training_event(attendees):
	return capkpi.get_doc(
		{
			"doctype": "Training Event",
			"event_name": "Basic Training Event",
			"training_program": "Basic Training",
			"location": "Union Square",
			"start_time": add_days(today(), 5),
			"end_time": add_days(today(), 6),
			"introduction": "Welcome to the Basic Training Event",
			"employees": attendees,
		}
	).insert()
