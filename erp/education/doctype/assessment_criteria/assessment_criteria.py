# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document

STD_CRITERIA = ["total", "total score", "total grade", "maximum score", "score", "grade"]


class AssessmentCriteria(Document):
	def validate(self):
		if self.assessment_criteria.lower() in STD_CRITERIA:
			capkpi.throw(_("Can't create standard criteria. Please rename the criteria"))
