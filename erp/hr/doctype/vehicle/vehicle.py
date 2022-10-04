# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import getdate


class Vehicle(Document):
	def validate(self):
		if getdate(self.start_date) > getdate(self.end_date):
			capkpi.throw(_("Insurance Start date should be less than Insurance End date"))
		if getdate(self.carbon_check_date) > getdate():
			capkpi.throw(_("Last carbon check date cannot be a future date"))


def get_timeline_data(doctype, name):
	"""Return timeline for vehicle log"""
	return dict(
		capkpi.db.sql(
			"""select unix_timestamp(date), count(*)
	from `tabVehicle Log` where license_plate=%s
	and date > date_sub(curdate(), interval 1 year)
	group by date""",
			name,
		)
	)
