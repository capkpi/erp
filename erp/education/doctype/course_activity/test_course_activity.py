# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestCourseActivity(unittest.TestCase):
	pass


def make_course_activity(enrollment, content_type, content):
	activity = capkpi.get_all(
		"Course Activity",
		filters={"enrollment": enrollment, "content_type": content_type, "content": content},
	)
	try:
		activity = capkpi.get_doc("Course Activity", activity[0]["name"])
	except (IndexError, capkpi.DoesNotExistError):
		activity = capkpi.get_doc(
			{
				"doctype": "Course Activity",
				"enrollment": enrollment,
				"content_type": content_type,
				"content": content,
				"activity_date": capkpi.utils.datetime.datetime.now(),
			}
		).insert()
	return activity
