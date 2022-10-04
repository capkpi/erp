# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.model.document import Document
from capkpi.utils import time_diff_in_hours


class DowntimeEntry(Document):
	def validate(self):
		if self.from_time and self.to_time:
			self.downtime = time_diff_in_hours(self.to_time, self.from_time) * 60
