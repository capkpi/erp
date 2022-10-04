# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi.model.document import Document
from capkpi.utils import getdate


class EmployeeAttendanceTool(Document):
	pass


@capkpi.whitelist()
def get_employees(date, department=None, branch=None, company=None):
	attendance_not_marked = []
	attendance_marked = []
	filters = {"status": "Active", "date_of_joining": ["<=", date]}

	for field, value in {"department": department, "branch": branch, "company": company}.items():
		if value:
			filters[field] = value

	employee_list = capkpi.get_list(
		"Employee", fields=["employee", "employee_name"], filters=filters, order_by="employee_name"
	)
	marked_employee = {}
	for emp in capkpi.get_list(
		"Attendance", fields=["employee", "status"], filters={"attendance_date": date}
	):
		marked_employee[emp["employee"]] = emp["status"]

	for employee in employee_list:
		employee["status"] = marked_employee.get(employee["employee"])
		if employee["employee"] not in marked_employee:
			attendance_not_marked.append(employee)
		else:
			attendance_marked.append(employee)
	return {"marked": attendance_marked, "unmarked": attendance_not_marked}


@capkpi.whitelist()
def mark_employee_attendance(employee_list, status, date, leave_type=None, company=None):

	employee_list = json.loads(employee_list)
	for employee in employee_list:

		if status == "On Leave" and leave_type:
			leave_type = leave_type
		else:
			leave_type = None

		company = capkpi.db.get_value("Employee", employee["employee"], "Company", cache=True)

		attendance = capkpi.get_doc(
			dict(
				doctype="Attendance",
				employee=employee.get("employee"),
				employee_name=employee.get("employee_name"),
				attendance_date=getdate(date),
				status=status,
				leave_type=leave_type,
				company=company,
			)
		)
		attendance.insert()
		attendance.submit()