# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from functools import reduce

import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import get_link_to_form


class CourseEnrollment(Document):
	def validate(self):
		self.validate_duplication()

	def get_progress(self, student):
		"""
		Returns Progress of given student for a particular course enrollment

		        :param self: Course Enrollment Object
		        :param student: Student Object
		"""
		course = capkpi.get_doc("Course", self.course)
		topics = course.get_topics()
		progress = []
		for topic in topics:
			progress.append(student.get_topic_progress(self.name, topic))
		if progress:
			return reduce(lambda x, y: x + y, progress)  # Flatten out the List
		else:
			return []

	def validate_duplication(self):
		enrollment = capkpi.db.exists(
			"Course Enrollment",
			{
				"student": self.student,
				"course": self.course,
				"program_enrollment": self.program_enrollment,
				"name": ("!=", self.name),
			},
		)
		if enrollment:
			capkpi.throw(
				_("Student is already enrolled via Course Enrollment {0}").format(
					get_link_to_form("Course Enrollment", enrollment)
				),
				title=_("Duplicate Entry"),
			)

	def add_quiz_activity(self, quiz_name, quiz_response, answers, score, status, time_taken):
		result = {k: ("Correct" if v else "Wrong") for k, v in answers.items()}
		result_data = []
		for key in answers:
			item = {}
			item["question"] = key
			item["quiz_result"] = result[key]
			try:
				if not quiz_response[key]:
					item["selected_option"] = "Unattempted"
				elif isinstance(quiz_response[key], list):
					item["selected_option"] = ", ".join(
						capkpi.get_value("Options", res, "option") for res in quiz_response[key]
					)
				else:
					item["selected_option"] = capkpi.get_value("Options", quiz_response[key], "option")
			except KeyError:
				item["selected_option"] = "Unattempted"
			result_data.append(item)

		quiz_activity = capkpi.get_doc(
			{
				"doctype": "Quiz Activity",
				"enrollment": self.name,
				"quiz": quiz_name,
				"activity_date": capkpi.utils.datetime.datetime.now(),
				"result": result_data,
				"score": score,
				"status": status,
				"time_taken": time_taken,
			}
		).insert(ignore_permissions=True)

	def add_activity(self, content_type, content):
		activity = check_activity_exists(self.name, content_type, content)
		if activity:
			return activity
		else:
			activity = capkpi.get_doc(
				{
					"doctype": "Course Activity",
					"enrollment": self.name,
					"content_type": content_type,
					"content": content,
					"activity_date": capkpi.utils.datetime.datetime.now(),
				}
			)

			activity.insert(ignore_permissions=True)
			return activity.name


def check_activity_exists(enrollment, content_type, content):
	activity = capkpi.get_all(
		"Course Activity",
		filters={"enrollment": enrollment, "content_type": content_type, "content": content},
	)
	if activity:
		return activity[0].name
	else:
		return None
