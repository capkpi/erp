# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document

from erp.hr.doctype.employee.employee import get_employee_emails


class TrainingResult(Document):
	def validate(self):
		training_event = capkpi.get_doc("Training Event", self.training_event)
		if training_event.docstatus != 1:
			capkpi.throw(_("{0} must be submitted").format(_("Training Event")))

		self.employee_emails = ", ".join(get_employee_emails([d.employee for d in self.employees]))

	def on_submit(self):
		training_event = capkpi.get_doc("Training Event", self.training_event)
		training_event.status = "Completed"
		for e in self.employees:
			for e1 in training_event.employees:
				if e1.employee == e.employee:
					e1.status = "Completed"
					break

		training_event.save()


@capkpi.whitelist()
def get_employees(training_event):
	return capkpi.get_doc("Training Event", training_event).employees
