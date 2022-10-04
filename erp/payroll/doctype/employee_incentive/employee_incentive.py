# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document

from erp.hr.utils import validate_active_employee


class EmployeeIncentive(Document):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_salary_structure()

	def validate_salary_structure(self):
		if not capkpi.db.exists("Salary Structure Assignment", {"employee": self.employee}):
			capkpi.throw(
				_("There is no Salary Structure assigned to {0}. First assign a Salary Stucture.").format(
					self.employee
				)
			)

	def on_submit(self):
		company = capkpi.db.get_value("Employee", self.employee, "company")

		additional_salary = capkpi.new_doc("Additional Salary")
		additional_salary.employee = self.employee
		additional_salary.currency = self.currency
		additional_salary.salary_component = self.salary_component
		additional_salary.overwrite_salary_structure_amount = 0
		additional_salary.amount = self.incentive_amount
		additional_salary.payroll_date = self.payroll_date
		additional_salary.company = company
		additional_salary.ref_doctype = self.doctype
		additional_salary.ref_docname = self.name
		additional_salary.submit()
