# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from datetime import timedelta

from capkpi.model.document import Document
from capkpi.utils import get_datetime


class RestaurantReservation(Document):
	def validate(self):
		if not self.reservation_end_time:
			self.reservation_end_time = get_datetime(self.reservation_time) + timedelta(hours=1)
