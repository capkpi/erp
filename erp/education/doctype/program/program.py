# Copyright (c) 2015, CapKPI Technologies and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class Program(Document):
	def get_course_list(self):
		program_course_list = self.courses
		course_list = [
			capkpi.get_doc("Course", program_course.course) for program_course in program_course_list
		]
		return course_list
