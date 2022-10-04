# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import formatdate, getdate

from erp.hr.utils import share_doc_with_approver, validate_active_employee


class OverlapError(capkpi.ValidationError):
	pass


class ShiftRequest(Document):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_dates()
		self.validate_shift_request_overlap_dates()
		self.validate_approver()
		self.validate_default_shift()

	def on_update(self):
		share_doc_with_approver(self, self.approver)

	def on_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			capkpi.throw(_("Only Shift Request with status 'Approved' and 'Rejected' can be submitted"))
		if self.status == "Approved":
			assignment_doc = capkpi.new_doc("Shift Assignment")
			assignment_doc.company = self.company
			assignment_doc.shift_type = self.shift_type
			assignment_doc.employee = self.employee
			assignment_doc.start_date = self.from_date
			if self.to_date:
				assignment_doc.end_date = self.to_date
			assignment_doc.shift_request = self.name
			assignment_doc.flags.ignore_permissions = 1
			assignment_doc.insert()
			assignment_doc.submit()

			capkpi.msgprint(
				_("Shift Assignment: {0} created for Employee: {1}").format(
					capkpi.bold(assignment_doc.name), capkpi.bold(self.employee)
				)
			)

	def on_cancel(self):
		shift_assignment_list = capkpi.get_list(
			"Shift Assignment", {"employee": self.employee, "shift_request": self.name}
		)
		if shift_assignment_list:
			for shift in shift_assignment_list:
				shift_assignment_doc = capkpi.get_doc("Shift Assignment", shift["name"])
				shift_assignment_doc.cancel()

	def validate_default_shift(self):
		default_shift = capkpi.get_value("Employee", self.employee, "default_shift")
		if self.shift_type == default_shift:
			capkpi.throw(
				_("You can not request for your Default Shift: {0}").format(capkpi.bold(self.shift_type))
			)

	def validate_approver(self):
		department = capkpi.get_value("Employee", self.employee, "department")
		shift_approver = capkpi.get_value("Employee", self.employee, "shift_request_approver")
		approvers = capkpi.db.sql(
			"""select approver from `tabDepartment Approver` where parent= %s and parentfield = 'shift_request_approver'""",
			(department),
		)
		approvers = [approver[0] for approver in approvers]
		approvers.append(shift_approver)
		if self.approver not in approvers:
			capkpi.throw(_("Only Approvers can Approve this Request."))

	def validate_dates(self):
		if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
			capkpi.throw(_("To date cannot be before from date"))

	def validate_shift_request_overlap_dates(self):
		if not self.name:
			self.name = "New Shift Request"

		d = capkpi.db.sql(
			"""
				select
					name, shift_type, from_date, to_date
				from `tabShift Request`
				where employee = %(employee)s and docstatus < 2
				and ((%(from_date)s >= from_date
					and %(from_date)s <= to_date) or
					( %(to_date)s >= from_date
					and %(to_date)s <= to_date ))
				and name != %(name)s""",
			{
				"employee": self.employee,
				"shift_type": self.shift_type,
				"from_date": self.from_date,
				"to_date": self.to_date,
				"name": self.name,
			},
			as_dict=1,
		)

		for date_overlap in d:
			if date_overlap["name"]:
				self.throw_overlap_error(date_overlap)

	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for {1} between {2} and {3} : ").format(
			self.employee, d["shift_type"], formatdate(d["from_date"]), formatdate(d["to_date"])
		) + """ <b><a href="/app/Form/Shift Request/{0}">{0}</a></b>""".format(d["name"])
		capkpi.throw(msg, OverlapError)
