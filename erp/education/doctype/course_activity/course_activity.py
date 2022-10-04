# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class CourseActivity(Document):
	def validate(self):
		self.check_if_enrolled()

	def check_if_enrolled(self):
		if capkpi.db.exists("Course Enrollment", self.enrollment):
			return True
		else:
			capkpi.throw(_("Course Enrollment {0} does not exists").format(self.enrollment))
