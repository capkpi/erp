# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

from erp.education.doctype.course_activity.test_course_activity import make_course_activity
from erp.education.doctype.program.test_program import setup_program
from erp.education.doctype.student.test_student import create_student, get_student


class TestCourseEnrollment(unittest.TestCase):
	def setUp(self):
		setup_program()
		student = create_student(
			{"first_name": "_Test First", "last_name": "_Test Last", "email": "_test_student_1@example.com"}
		)
		program_enrollment = student.enroll_in_program("_Test Program")
		course_enrollment = capkpi.db.get_value(
			"Course Enrollment",
			{
				"course": "_Test Course 1",
				"student": student.name,
				"program_enrollment": program_enrollment.name,
			},
			"name",
		)
		make_course_activity(course_enrollment, "Article", "_Test Article 1-1")

	def test_get_progress(self):
		student = get_student("_test_student_1@example.com")
		program_enrollment_name = capkpi.get_list(
			"Program Enrollment", filters={"student": student.name, "Program": "_Test Program"}
		)[0].name
		course_enrollment_name = capkpi.get_list(
			"Course Enrollment",
			filters={
				"student": student.name,
				"course": "_Test Course 1",
				"program_enrollment": program_enrollment_name,
			},
		)[0].name
		course_enrollment = capkpi.get_doc("Course Enrollment", course_enrollment_name)
		progress = course_enrollment.get_progress(student)
		finished = {"content": "_Test Article 1-1", "content_type": "Article", "is_complete": True}
		self.assertTrue(finished in progress)
		capkpi.db.rollback()

	def tearDown(self):
		for entry in capkpi.db.get_all("Course Enrollment"):
			capkpi.delete_doc("Course Enrollment", entry.name)

		for entry in capkpi.db.get_all("Program Enrollment"):
			doc = capkpi.get_doc("Program Enrollment", entry.name)
			doc.cancel()
			doc.delete()