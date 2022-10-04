# Copyright (c) 2015, CapKPI Technologies and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import formatdate, get_link_to_form, getdate

from erp import get_default_company
from erp.education.api import get_student_group_students
from erp.hr.doctype.holiday_list.holiday_list import is_holiday


class StudentAttendance(Document):
	def validate(self):
		self.validate_mandatory()
		self.validate_date()
		self.set_date()
		self.set_student_group()
		self.validate_student()
		self.validate_duplication()
		self.validate_is_holiday()

	def set_date(self):
		if self.course_schedule:
			self.date = capkpi.db.get_value("Course Schedule", self.course_schedule, "schedule_date")

	def validate_mandatory(self):
		if not (self.student_group or self.course_schedule):
			capkpi.throw(
				_("{0} or {1} is mandatory").format(
					capkpi.bold("Student Group"), capkpi.bold("Course Schedule")
				),
				title=_("Mandatory Fields"),
			)

	def validate_date(self):
		if not self.leave_application and getdate(self.date) > getdate():
			capkpi.throw(_("Attendance cannot be marked for future dates."))

		if self.student_group:
			academic_year = capkpi.db.get_value("Student Group", self.student_group, "academic_year")
			if academic_year:
				year_start_date, year_end_date = capkpi.db.get_value(
					"Academic Year", academic_year, ["year_start_date", "year_end_date"]
				)
				if year_start_date and year_end_date:
					if getdate(self.date) < getdate(year_start_date) or getdate(self.date) > getdate(
						year_end_date
					):
						capkpi.throw(
							_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
						)

	def set_student_group(self):
		if self.course_schedule:
			self.student_group = capkpi.db.get_value(
				"Course Schedule", self.course_schedule, "student_group"
			)

	def validate_student(self):
		if self.course_schedule:
			student_group = capkpi.db.get_value("Course Schedule", self.course_schedule, "student_group")
		else:
			student_group = self.student_group
		student_group_students = [d.student for d in get_student_group_students(student_group)]
		if student_group and self.student not in student_group_students:
			student_group_doc = get_link_to_form("Student Group", student_group)
			capkpi.throw(
				_("Student {0}: {1} does not belong to Student Group {2}").format(
					capkpi.bold(self.student), self.student_name, capkpi.bold(student_group_doc)
				)
			)

	def validate_duplication(self):
		"""Check if the Attendance Record is Unique"""
		attendance_record = None
		if self.course_schedule:
			attendance_record = capkpi.db.exists(
				"Student Attendance",
				{
					"student": self.student,
					"course_schedule": self.course_schedule,
					"docstatus": ("!=", 2),
					"name": ("!=", self.name),
				},
			)
		else:
			attendance_record = capkpi.db.exists(
				"Student Attendance",
				{
					"student": self.student,
					"student_group": self.student_group,
					"date": self.date,
					"docstatus": ("!=", 2),
					"name": ("!=", self.name),
					"course_schedule": "",
				},
			)

		if attendance_record:
			record = get_link_to_form("Student Attendance", attendance_record)
			capkpi.throw(
				_("Student Attendance record {0} already exists against the Student {1}").format(
					record, capkpi.bold(self.student)
				),
				title=_("Duplicate Entry"),
			)

	def validate_is_holiday(self):
		holiday_list = get_holiday_list()
		if is_holiday(holiday_list, self.date):
			capkpi.throw(
				_("Attendance cannot be marked for {0} as it is a holiday.").format(
					capkpi.bold(formatdate(self.date))
				)
			)


def get_holiday_list(company=None):
	if not company:
		company = get_default_company() or capkpi.get_all("Company")[0].name

	holiday_list = capkpi.get_cached_value("Company", company, "default_holiday_list")
	if not holiday_list:
		capkpi.throw(
			_("Please set a default Holiday List for Company {0}").format(
				capkpi.bold(get_default_company())
			)
		)
	return holiday_list
