# Copyright (c) 2015, CapKPI Technologies and Contributors
# See license.txt

import unittest

import capkpi

from erp.education.doctype.topic.test_topic import make_topic, make_topic_and_linked_content

# test_records = capkpi.get_test_records('Course')


class TestCourse(unittest.TestCase):
	def setUp(self):
		make_topic_and_linked_content("_Test Topic 1", [{"type": "Article", "name": "_Test Article 1"}])
		make_topic_and_linked_content("_Test Topic 2", [{"type": "Article", "name": "_Test Article 2"}])
		make_course_and_linked_topic("_Test Course 1", ["_Test Topic 1", "_Test Topic 2"])

	def test_get_topics(self):
		course = capkpi.get_doc("Course", "_Test Course 1")
		topics = course.get_topics()
		self.assertEqual(topics[0].name, "_Test Topic 1")
		self.assertEqual(topics[1].name, "_Test Topic 2")
		capkpi.db.rollback()


def make_course(name):
	try:
		course = capkpi.get_doc("Course", name)
	except capkpi.DoesNotExistError:
		course = capkpi.get_doc({"doctype": "Course", "course_name": name, "course_code": name}).insert()
	return course.name


def make_course_and_linked_topic(course_name, topic_name_list):
	try:
		course = capkpi.get_doc("Course", course_name)
	except capkpi.DoesNotExistError:
		make_course(course_name)
		course = capkpi.get_doc("Course", course_name)
	topic_list = [make_topic(topic_name) for topic_name in topic_name_list]
	for topic in topic_list:
		course.append("topics", {"topic": topic})
	course.save()
	return course
