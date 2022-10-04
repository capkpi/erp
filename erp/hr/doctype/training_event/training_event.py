# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import time_diff_in_seconds

from erp.hr.doctype.employee.employee import get_employee_emails


class TrainingEvent(Document):
	def validate(self):
		self.set_employee_emails()
		self.validate_period()

	def on_update_after_submit(self):
		self.set_status_for_attendees()

	def set_employee_emails(self):
		self.employee_emails = ", ".join(get_employee_emails([d.employee for d in self.employees]))

	def validate_period(self):
		if time_diff_in_seconds(self.end_time, self.start_time) <= 0:
			capkpi.throw(_("End time cannot be before start time"))

	def set_status_for_attendees(self):
		if self.event_status == "Completed":
			for employee in self.employees:
				if employee.attendance == "Present" and employee.status != "Feedback Submitted":
					employee.status = "Completed"

		elif self.event_status == "Scheduled":
			for employee in self.employees:
				employee.status = "Open"

		self.db_update_all()
