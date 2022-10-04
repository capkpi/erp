# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import nowdate

from erp.hr.doctype.employee_onboarding.employee_onboarding import (
	IncompleteTaskError,
	make_employee,
)
from erp.hr.doctype.job_offer.test_job_offer import create_job_offer


class TestEmployeeOnboarding(unittest.TestCase):
	def test_employee_onboarding_incomplete_task(self):
		if capkpi.db.exists("Employee Onboarding", {"employee_name": "Test Researcher"}):
			capkpi.delete_doc("Employee Onboarding", {"employee_name": "Test Researcher"})
		capkpi.db.sql("delete from `tabEmployee Onboarding`")
		project = "Employee Onboarding : test@researcher.com"
		capkpi.db.sql("delete from tabProject where name=%s", project)
		capkpi.db.sql("delete from tabTask where project=%s", project)
		applicant = get_job_applicant()

		job_offer = create_job_offer(job_applicant=applicant.name)
		job_offer.submit()

		onboarding = capkpi.new_doc("Employee Onboarding")
		onboarding.job_applicant = applicant.name
		onboarding.job_offer = job_offer.name
		onboarding.company = "_Test Company"
		onboarding.designation = "Researcher"
		onboarding.append(
			"activities",
			{"activity_name": "Assign ID Card", "role": "HR User", "required_for_employee_creation": 1},
		)
		onboarding.append("activities", {"activity_name": "Assign a laptop", "role": "HR User"})
		onboarding.status = "Pending"
		onboarding.insert()
		onboarding.submit()

		project_name = capkpi.db.get_value("Project", onboarding.project, "project_name")
		self.assertEqual(project_name, "Employee Onboarding : test@researcher.com")

		# don't allow making employee if onboarding is not complete
		self.assertRaises(IncompleteTaskError, make_employee, onboarding.name)

		# complete the task
		project = capkpi.get_doc("Project", onboarding.project)
		for task in capkpi.get_all("Task", dict(project=project.name)):
			task = capkpi.get_doc("Task", task.name)
			task.status = "Completed"
			task.save()

		# make employee
		onboarding.reload()
		employee = make_employee(onboarding.name)
		employee.first_name = employee.employee_name
		employee.date_of_joining = nowdate()
		employee.date_of_birth = "1990-05-08"
		employee.gender = "Female"
		employee.insert()
		self.assertEqual(employee.employee_name, "Test Researcher")


def get_job_applicant():
	if capkpi.db.exists("Job Applicant", "test@researcher.com"):
		return capkpi.get_doc("Job Applicant", "test@researcher.com")
	applicant = capkpi.new_doc("Job Applicant")
	applicant.applicant_name = "Test Researcher"
	applicant.email_id = "test@researcher.com"
	applicant.designation = "Researcher"
	applicant.status = "Open"
	applicant.cover_letter = "I am a great Researcher."
	applicant.insert()
	return applicant


def _set_up():
	for doctype in ["Employee Onboarding"]:
		capkpi.db.sql("delete from `tab{doctype}`".format(doctype=doctype))

	project = "Employee Onboarding : Test Researcher - test@researcher.com"
	capkpi.db.sql("delete from tabProject where name=%s", project)
	capkpi.db.sql("delete from tabTask where project=%s", project)
