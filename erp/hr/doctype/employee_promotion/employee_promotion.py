# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import getdate

from erp.hr.utils import update_employee_work_history, validate_active_employee


class EmployeePromotion(Document):
	def validate(self):
		validate_active_employee(self.employee)

	def before_submit(self):
		if getdate(self.promotion_date) > getdate():
			capkpi.throw(
				_("Employee Promotion cannot be submitted before Promotion Date"),
				capkpi.DocstatusTransitionError,
			)

	def on_submit(self):
		employee = capkpi.get_doc("Employee", self.employee)
		employee = update_employee_work_history(
			employee, self.promotion_details, date=self.promotion_date
		)
		employee.save()

	def on_cancel(self):
		employee = capkpi.get_doc("Employee", self.employee)
		employee = update_employee_work_history(employee, self.promotion_details, cancel=True)
		employee.save()
