# Copyright (c) 2015, CapKPI Technologies and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi import _
from capkpi.email.doctype.email_group.email_group import add_subscribers
from capkpi.model.mapper import get_mapped_doc
from capkpi.utils import cstr, flt, getdate


def get_course(program):
	"""Return list of courses for a particular program
	:param program: Program
	"""
	courses = capkpi.db.sql(
		"""select course, course_name from `tabProgram Course` where parent=%s""", (program), as_dict=1
	)
	return courses


@capkpi.whitelist()
def enroll_student(source_name):
	"""Creates a Student Record and returns a Program Enrollment.

	:param source_name: Student Applicant.
	"""
	capkpi.publish_realtime("enroll_student_progress", {"progress": [1, 4]}, user=capkpi.session.user)
	student = get_mapped_doc(
		"Student Applicant",
		source_name,
		{"Student Applicant": {"doctype": "Student", "field_map": {"name": "student_applicant"}}},
		ignore_permissions=True,
	)
	student.save()

	student_applicant = capkpi.db.get_value(
		"Student Applicant", source_name, ["student_category", "program"], as_dict=True
	)
	program_enrollment = capkpi.new_doc("Program Enrollment")
	program_enrollment.student = student.name
	program_enrollment.student_category = student_applicant.student_category
	program_enrollment.student_name = student.title
	program_enrollment.program = student_applicant.program
	capkpi.publish_realtime("enroll_student_progress", {"progress": [2, 4]}, user=capkpi.session.user)
	return program_enrollment


@capkpi.whitelist()
def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
	"""Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if course_schedule:
		return capkpi.get_list("Student Attendance", filters={"course_schedule": course_schedule})
	else:
		return capkpi.get_list(
			"Student Attendance", filters={"student_group": student_group, "date": date}
		)


@capkpi.whitelist()
def mark_attendance(
	students_present, students_absent, course_schedule=None, student_group=None, date=None
):
	"""Creates Multiple Attendance Records.

	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""

	if student_group:
		academic_year = capkpi.db.get_value("Student Group", student_group, "academic_year")
		if academic_year:
			year_start_date, year_end_date = capkpi.db.get_value(
				"Academic Year", academic_year, ["year_start_date", "year_end_date"]
			)
			if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(year_end_date):
				capkpi.throw(
					_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
				)

	present = json.loads(students_present)
	absent = json.loads(students_absent)

	for d in present:
		make_attendance_records(
			d["student"], d["student_name"], "Present", course_schedule, student_group, date
		)

	for d in absent:
		make_attendance_records(
			d["student"], d["student_name"], "Absent", course_schedule, student_group, date
		)

	capkpi.db.commit()
	capkpi.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(
	student, student_name, status, course_schedule=None, student_group=None, date=None
):
	"""Creates/Update Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent)
	"""
	student_attendance = capkpi.get_doc(
		{
			"doctype": "Student Attendance",
			"student": student,
			"course_schedule": course_schedule,
			"student_group": student_group,
			"date": date,
		}
	)
	if not student_attendance:
		student_attendance = capkpi.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.save()
	student_attendance.submit()


@capkpi.whitelist()
def get_student_guardians(student):
	"""Returns List of Guardians of a Student.

	:param student: Student.
	"""
	guardians = capkpi.get_all("Student Guardian", fields=["guardian"], filters={"parent": student})
	return guardians


@capkpi.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	"""Returns List of student, student_name in Student Group.

	:param student_group: Student Group.
	"""
	if include_inactive:
		students = capkpi.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group},
			order_by="group_roll_number",
		)
	else:
		students = capkpi.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group, "active": 1},
			order_by="group_roll_number",
		)
	return students


@capkpi.whitelist()
def get_fee_structure(program, academic_term=None):
	"""Returns Fee Structure.

	:param program: Program.
	:param academic_term: Academic Term.
	"""
	fee_structure = capkpi.db.get_values(
		"Fee Structure", {"program": program, "academic_term": academic_term}, "name", as_dict=True
	)
	return fee_structure[0].name if fee_structure else None


@capkpi.whitelist()
def get_fee_components(fee_structure):
	"""Returns Fee Components.

	:param fee_structure: Fee Structure.
	"""
	if fee_structure:
		fs = capkpi.get_all(
			"Fee Component",
			fields=["fees_category", "description", "amount"],
			filters={"parent": fee_structure},
			order_by="idx",
		)
		return fs


@capkpi.whitelist()
def get_fee_schedule(program, student_category=None, academic_year=None):
	"""Returns Fee Schedule.
	:param program: Program.
	:param student_category: Student Category.
	:param academic_year: Academic Year.
	"""
	filters = {}
	if program:
		filters = {"program": program}

	if student_category:
		filters["student_category"] = student_category

	if academic_year:
		filters["academic_year"] = academic_year

	fs = capkpi.db.get_list(
		"Fee Schedule",
		filters=filters,
		fields=[
			"academic_term",
			"fee_structure",
			"student_category",
			"due_date",
			"total_amount as amount",
		],
		order_by="idx",
	)
	return fs


@capkpi.whitelist()
def collect_fees(fees, amt):
	paid_amount = flt(amt) + flt(capkpi.db.get_value("Fees", fees, "paid_amount"))
	total_amount = flt(capkpi.db.get_value("Fees", fees, "total_amount"))
	capkpi.db.set_value("Fees", fees, "paid_amount", paid_amount)
	capkpi.db.set_value("Fees", fees, "outstanding_amount", (total_amount - paid_amount))
	return paid_amount


@capkpi.whitelist()
def get_course_schedule_events(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from capkpi.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Course Schedule", filters)

	data = capkpi.db.sql(
		"""select name, course, color,
			timestamp(schedule_date, from_time) as from_time,
			timestamp(schedule_date, to_time) as to_time,
			room, student_group, 0 as 'allDay'
		from `tabCourse Schedule`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	return data


@capkpi.whitelist()
def get_assessment_criteria(course):
	"""Returns Assessmemt Criteria and their Weightage from Course Master.

	:param Course: Course
	"""
	return capkpi.get_all(
		"Course Assessment Criteria",
		fields=["assessment_criteria", "weightage"],
		filters={"parent": course},
		order_by="idx",
	)


@capkpi.whitelist()
def get_assessment_students(assessment_plan, student_group):
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		result = get_result(student.student, assessment_plan)
		if result:
			student_result = {}
			for d in result.details:
				student_result.update({d.assessment_criteria: [cstr(d.score), d.grade]})
			student_result.update(
				{"total_score": [cstr(result.total_score), result.grade], "comment": result.comment}
			)
			student.update(
				{"assessment_details": student_result, "docstatus": result.docstatus, "name": result.name}
			)
		else:
			student.update({"assessment_details": None})
	return student_list


@capkpi.whitelist()
def get_assessment_details(assessment_plan):
	"""Returns Assessment Criteria  and Maximum Score from Assessment Plan Master.

	:param Assessment Plan: Assessment Plan
	"""
	return capkpi.get_all(
		"Assessment Plan Criteria",
		fields=["assessment_criteria", "maximum_score", "docstatus"],
		filters={"parent": assessment_plan},
		order_by="idx",
	)


@capkpi.whitelist()
def get_result(student, assessment_plan):
	"""Returns Submitted Result of given student for specified Assessment Plan

	:param Student: Student
	:param Assessment Plan: Assessment Plan
	"""
	results = capkpi.get_all(
		"Assessment Result",
		filters={"student": student, "assessment_plan": assessment_plan, "docstatus": ("!=", 2)},
	)
	if results:
		return capkpi.get_doc("Assessment Result", results[0])
	else:
		return None


@capkpi.whitelist()
def get_grade(grading_scale, percentage):
	"""Returns Grade based on the Grading Scale and Score.

	:param Grading Scale: Grading Scale
	:param Percentage: Score Percentage Percentage
	"""
	grading_scale_intervals = {}
	if not hasattr(capkpi.local, "grading_scale"):
		grading_scale = capkpi.get_all(
			"Grading Scale Interval", fields=["grade_code", "threshold"], filters={"parent": grading_scale}
		)
		capkpi.local.grading_scale = grading_scale
	for d in capkpi.local.grading_scale:
		grading_scale_intervals.update({d.threshold: d.grade_code})
	intervals = sorted(grading_scale_intervals.keys(), key=float, reverse=True)
	for interval in intervals:
		if flt(percentage) >= interval:
			grade = grading_scale_intervals.get(interval)
			break
		else:
			grade = ""
	return grade


@capkpi.whitelist()
def mark_assessment_result(assessment_plan, scores):
	student_score = json.loads(scores)
	assessment_details = []
	for criteria in student_score.get("assessment_details"):
		assessment_details.append(
			{"assessment_criteria": criteria, "score": flt(student_score["assessment_details"][criteria])}
		)
	assessment_result = get_assessment_result_doc(student_score["student"], assessment_plan)
	assessment_result.update(
		{
			"student": student_score.get("student"),
			"assessment_plan": assessment_plan,
			"comment": student_score.get("comment"),
			"total_score": student_score.get("total_score"),
			"details": assessment_details,
		}
	)
	assessment_result.save()
	details = {}
	for d in assessment_result.details:
		details.update({d.assessment_criteria: d.grade})
	assessment_result_dict = {
		"name": assessment_result.name,
		"student": assessment_result.student,
		"total_score": assessment_result.total_score,
		"grade": assessment_result.grade,
		"details": details,
	}
	return assessment_result_dict


@capkpi.whitelist()
def submit_assessment_results(assessment_plan, student_group):
	total_result = 0
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		doc = get_result(student.student, assessment_plan)
		if doc and doc.docstatus == 0:
			total_result += 1
			doc.submit()
	return total_result


def get_assessment_result_doc(student, assessment_plan):
	assessment_result = capkpi.get_all(
		"Assessment Result",
		filters={"student": student, "assessment_plan": assessment_plan, "docstatus": ("!=", 2)},
	)
	if assessment_result:
		doc = capkpi.get_doc("Assessment Result", assessment_result[0])
		if doc.docstatus == 0:
			return doc
		elif doc.docstatus == 1:
			capkpi.msgprint(_("Result already Submitted"))
			return None
	else:
		return capkpi.new_doc("Assessment Result")


@capkpi.whitelist()
def update_email_group(doctype, name):
	if not capkpi.db.exists("Email Group", name):
		email_group = capkpi.new_doc("Email Group")
		email_group.title = name
		email_group.save()
	email_list = []
	students = []
	if doctype == "Student Group":
		students = get_student_group_students(name)
	for stud in students:
		for guard in get_student_guardians(stud.student):
			email = capkpi.db.get_value("Guardian", guard.guardian, "email_address")
			if email:
				email_list.append(email)
	add_subscribers(name, email_list)


@capkpi.whitelist()
def get_current_enrollment(student, academic_year=None):
	current_academic_year = academic_year or capkpi.defaults.get_defaults().academic_year
	program_enrollment_list = capkpi.db.sql(
		"""
		select
			name as program_enrollment, student_name, program, student_batch_name as student_batch,
			student_category, academic_term, academic_year
		from
			`tabProgram Enrollment`
		where
			student = %s and academic_year = %s
		order by creation""",
		(student, current_academic_year),
		as_dict=1,
	)

	if program_enrollment_list:
		return program_enrollment_list[0]
	else:
		return None
