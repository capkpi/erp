# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.tests.utils import CapKPITestCase
from capkpi.utils import add_days, getdate

from erp.hr.doctype.employee.test_employee import make_employee
from erp.hr.doctype.staffing_plan.test_staffing_plan import make_company


class TestJobOpening(CapKPITestCase):
	def setUp(self):
		capkpi.db.delete("Staffing Plan")
		capkpi.db.delete("Staffing Plan Detail")
		capkpi.db.delete("Job Opening")

		make_company("_Test Opening Company", "_TOC")
		capkpi.db.delete("Employee", {"company": "_Test Opening Company"})

	def test_vacancies_fulfilled(self):
		make_employee(
			"test_job_opening@example.com", company="_Test Opening Company", designation="Designer"
		)

		staffing_plan = capkpi.get_doc(
			{
				"doctype": "Staffing Plan",
				"company": "_Test Opening Company",
				"name": "Test",
				"from_date": getdate(),
				"to_date": add_days(getdate(), 10),
			}
		)

		staffing_plan.append(
			"staffing_details",
			{"designation": "Designer", "vacancies": 1, "estimated_cost_per_position": 50000},
		)
		staffing_plan.insert()
		staffing_plan.submit()

		self.assertEqual(staffing_plan.staffing_details[0].number_of_positions, 2)

		# allows creating 1 job opening as per vacancy
		opening_1 = get_job_opening()
		opening_1.insert()

		# vacancies as per staffing plan already fulfilled via job opening and existing employee count
		opening_2 = get_job_opening(job_title="Designer New")
		self.assertRaises(capkpi.ValidationError, opening_2.insert)

		# allows updating existing job opening
		opening_1.status = "Closed"
		opening_1.save()


def get_job_opening(**args):
	args = capkpi._dict(args)

	opening = capkpi.db.exists("Job Opening", {"job_title": args.job_title or "Designer"})
	if opening:
		return capkpi.get_doc("Job Opening", opening)

	opening = capkpi.get_doc(
		{
			"doctype": "Job Opening",
			"job_title": "Designer",
			"designation": "Designer",
			"company": "_Test Opening Company",
			"status": "Open",
		}
	)

	opening.update(args)

	return opening
