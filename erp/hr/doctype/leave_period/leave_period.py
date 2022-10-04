# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import getdate

from erp.hr.utils import validate_overlap


class LeavePeriod(Document):
	def validate(self):
		self.validate_dates()
		validate_overlap(self, self.from_date, self.to_date, self.company)

	def validate_dates(self):
		if getdate(self.from_date) >= getdate(self.to_date):
			capkpi.throw(_("To date can not be equal or less than from date"))
