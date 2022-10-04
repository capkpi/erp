# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import cint


class GradingScale(Document):
	def validate(self):
		thresholds = []
		for d in self.intervals:
			if d.threshold in thresholds:
				capkpi.throw(_("Treshold {0}% appears more than once").format(d.threshold))
			else:
				thresholds.append(cint(d.threshold))
		if 0 not in thresholds:
			capkpi.throw(_("Please define grade for Threshold 0%"))
