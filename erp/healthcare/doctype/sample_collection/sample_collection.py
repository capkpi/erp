# Copyright (c) 2015, ESS and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import flt


class SampleCollection(Document):
	def validate(self):
		if flt(self.sample_qty) <= 0:
			capkpi.throw(_("Sample Quantity cannot be negative or 0"), title=_("Invalid Quantity"))
