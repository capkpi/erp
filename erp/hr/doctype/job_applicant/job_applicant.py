# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.model.naming import append_number_if_name_exists
from capkpi.utils import validate_email_address

from erp.hr.doctype.interview.interview import get_interviewers


class DuplicationError(capkpi.ValidationError):
	pass


class JobApplicant(Document):
	def onload(self):
		job_offer = capkpi.get_all("Job Offer", filters={"job_applicant": self.name})
		if job_offer:
			self.get("__onload").job_offer = job_offer[0].name

	def autoname(self):
		self.name = self.email_id

		# applicant can apply more than once for a different job title or reapply
		if capkpi.db.exists("Job Applicant", self.name):
			self.name = append_number_if_name_exists("Job Applicant", self.name)

	def validate(self):
		if self.email_id:
			validate_email_address(self.email_id, True)

		if self.employee_referral:
			self.set_status_for_employee_referral()

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split("@")[0]
			self.applicant_name = " ".join([p.capitalize() for p in guess.split(".")])

	def set_status_for_employee_referral(self):
		emp_ref = capkpi.get_doc("Employee Referral", self.employee_referral)
		if self.status in ["Open", "Replied", "Hold"]:
			emp_ref.db_set("status", "In Process")
		elif self.status in ["Accepted", "Rejected"]:
			emp_ref.db_set("status", self.status)


@capkpi.whitelist()
def create_interview(doc, interview_round):
	import json

	from six import string_types

	if isinstance(doc, string_types):
		doc = json.loads(doc)
		doc = capkpi.get_doc(doc)

	round_designation = capkpi.db.get_value("Interview Round", interview_round, "designation")

	if round_designation and doc.designation and round_designation != doc.designation:
		capkpi.throw(
			_("Interview Round {0} is only applicable for the Designation {1}").format(
				interview_round, round_designation
			)
		)

	interview = capkpi.new_doc("Interview")
	interview.interview_round = interview_round
	interview.job_applicant = doc.name
	interview.designation = doc.designation
	interview.resume_link = doc.resume_link
	interview.job_opening = doc.job_title
	interviewer_detail = get_interviewers(interview_round)

	for d in interviewer_detail:
		interview.append("interview_details", {"interviewer": d.interviewer})
	return interview


@capkpi.whitelist()
def get_interview_details(job_applicant):
	interview_details = capkpi.db.get_all(
		"Interview",
		filters={"job_applicant": job_applicant, "docstatus": ["!=", 2]},
		fields=["name", "interview_round", "expected_average_rating", "average_rating", "status"],
	)
	interview_detail_map = {}

	for detail in interview_details:
		interview_detail_map[detail.name] = detail

	return interview_detail_map
