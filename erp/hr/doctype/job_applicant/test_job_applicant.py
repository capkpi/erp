# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and Contributors
# See license.txt

import unittest

import capkpi

from erp.hr.doctype.designation.test_designation import create_designation


class TestJobApplicant(unittest.TestCase):
	def test_job_applicant_naming(self):
		applicant = capkpi.get_doc(
			{
				"doctype": "Job Applicant",
				"status": "Open",
				"applicant_name": "_Test Applicant",
				"email_id": "job_applicant_naming@example.com",
			}
		).insert()
		self.assertEqual(applicant.name, "job_applicant_naming@example.com")

		applicant = capkpi.get_doc(
			{
				"doctype": "Job Applicant",
				"status": "Open",
				"applicant_name": "_Test Applicant",
				"email_id": "job_applicant_naming@example.com",
			}
		).insert()
		self.assertEqual(applicant.name, "job_applicant_naming@example.com-1")

	def tearDown(self):
		capkpi.db.rollback()


def create_job_applicant(**args):
	args = capkpi._dict(args)

	filters = {
		"applicant_name": args.applicant_name or "_Test Applicant",
		"email_id": args.email_id or "test_applicant@example.com",
	}

	if capkpi.db.exists("Job Applicant", filters):
		return capkpi.get_doc("Job Applicant", filters)

	job_applicant = capkpi.get_doc(
		{
			"doctype": "Job Applicant",
			"status": args.status or "Open",
			"designation": create_designation().name,
		}
	)

	job_applicant.update(filters)
	job_applicant.save()

	return job_applicant
