# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class TrainingFeedback(Document):
	def validate(self):
		training_event = capkpi.get_doc("Training Event", self.training_event)
		if training_event.docstatus != 1:
			capkpi.throw(_("{0} must be submitted").format(_("Training Event")))

		emp_event_details = capkpi.db.get_value(
			"Training Event Employee",
			{"parent": self.training_event, "employee": self.employee},
			["name", "attendance"],
			as_dict=True,
		)

		if not emp_event_details:
			capkpi.throw(
				_("Employee {0} not found in Training Event Participants.").format(
					capkpi.bold(self.employee_name)
				)
			)

		if emp_event_details.attendance == "Absent":
			capkpi.throw(_("Feedback cannot be recorded for an absent Employee."))

	def on_submit(self):
		employee = capkpi.db.get_value(
			"Training Event Employee", {"parent": self.training_event, "employee": self.employee}
		)

		if employee:
			capkpi.db.set_value("Training Event Employee", employee, "status", "Feedback Submitted")

	def on_cancel(self):
		employee = capkpi.db.get_value(
			"Training Event Employee", {"parent": self.training_event, "employee": self.employee}
		)

		if employee:
			capkpi.db.set_value("Training Event Employee", employee, "status", "Completed")
