# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import cint, flt


class AppraisalTemplate(Document):
	def validate(self):
		self.check_total_points()

	def check_total_points(self):
		total_points = 0
		for d in self.get("goals"):
			total_points += flt(d.per_weightage)

		if cint(total_points) != 100:
			capkpi.throw(_("Sum of points for all goals should be 100. It is {0}").format(total_points))
