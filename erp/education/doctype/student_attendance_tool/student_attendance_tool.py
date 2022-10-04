# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class StudentAttendanceTool(Document):
	pass


@capkpi.whitelist()
def get_student_attendance_records(based_on, date=None, student_group=None, course_schedule=None):
	student_list = []
	student_attendance_list = []

	if based_on == "Course Schedule":
		student_group = capkpi.db.get_value("Course Schedule", course_schedule, "student_group")
		if student_group:
			student_list = capkpi.get_all(
				"Student Group Student",
				fields=["student", "student_name", "group_roll_number"],
				filters={"parent": student_group, "active": 1},
				order_by="group_roll_number",
			)

	if not student_list:
		student_list = capkpi.get_all(
			"Student Group Student",
			fields=["student", "student_name", "group_roll_number"],
			filters={"parent": student_group, "active": 1},
			order_by="group_roll_number",
		)

	table = capkpi.qb.DocType("Student Attendance")

	if course_schedule:
		student_attendance_list = (
			capkpi.qb.from_(table)
			.select(table.student, table.status)
			.where((table.course_schedule == course_schedule))
		).run(as_dict=True)
	else:
		student_attendance_list = (
			capkpi.qb.from_(table)
			.select(table.student, table.status)
			.where(
				(table.student_group == student_group) & (table.date == date) & (table.course_schedule == "")
				| (table.course_schedule.isnull())
			)
		).run(as_dict=True)

	for attendance in student_attendance_list:
		for student in student_list:
			if student.student == attendance.student:
				student.status = attendance.status

	return student_list
