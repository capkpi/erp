# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import flt, get_link_to_form, getdate


class InterviewFeedback(Document):
	def validate(self):
		self.validate_interviewer()
		self.validate_interview_date()
		self.validate_duplicate()
		self.calculate_average_rating()

	def on_submit(self):
		self.update_interview_details()

	def on_cancel(self):
		self.update_interview_details()

	def validate_interviewer(self):
		applicable_interviewers = get_applicable_interviewers(self.interview)
		if self.interviewer not in applicable_interviewers:
			capkpi.throw(
				_("{0} is not allowed to submit Interview Feedback for the Interview: {1}").format(
					capkpi.bold(self.interviewer), capkpi.bold(self.interview)
				)
			)

	def validate_interview_date(self):
		scheduled_date = capkpi.db.get_value("Interview", self.interview, "scheduled_on")

		if getdate() < getdate(scheduled_date) and self.docstatus == 1:
			capkpi.throw(
				_("{0} submission before {1} is not allowed").format(
					capkpi.bold("Interview Feedback"), capkpi.bold("Interview Scheduled Date")
				)
			)

	def validate_duplicate(self):
		duplicate_feedback = capkpi.db.exists(
			"Interview Feedback",
			{"interviewer": self.interviewer, "interview": self.interview, "docstatus": 1},
		)

		if duplicate_feedback:
			capkpi.throw(
				_(
					"Feedback already submitted for the Interview {0}. Please cancel the previous Interview Feedback {1} to continue."
				).format(
					self.interview, get_link_to_form("Interview Feedback", duplicate_feedback)
				)
			)

	def calculate_average_rating(self):
		total_rating = 0
		for d in self.skill_assessment:
			if d.rating:
				total_rating += d.rating

		self.average_rating = flt(
			total_rating / len(self.skill_assessment) if len(self.skill_assessment) else 0
		)

	def update_interview_details(self):
		doc = capkpi.get_doc("Interview", self.interview)
		total_rating = 0

		if self.docstatus == 2:
			for entry in doc.interview_details:
				if entry.interview_feedback == self.name:
					entry.average_rating = entry.interview_feedback = entry.comments = entry.result = None
					break
		else:
			for entry in doc.interview_details:
				if entry.interviewer == self.interviewer:
					entry.average_rating = self.average_rating
					entry.interview_feedback = self.name
					entry.comments = self.feedback
					entry.result = self.result

				if entry.average_rating:
					total_rating += entry.average_rating

		doc.average_rating = flt(
			total_rating / len(doc.interview_details) if len(doc.interview_details) else 0
		)
		doc.save()
		doc.notify_update()


@capkpi.whitelist()
def get_applicable_interviewers(interview):
	data = capkpi.get_all("Interview Detail", filters={"parent": interview}, fields=["interviewer"])
	return [d.interviewer for d in data]
