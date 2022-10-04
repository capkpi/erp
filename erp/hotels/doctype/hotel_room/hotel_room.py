# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class HotelRoom(Document):
	def validate(self):
		if not self.capacity:
			self.capacity, self.extra_bed_capacity = capkpi.db.get_value(
				"Hotel Room Type", self.hotel_room_type, ["capacity", "extra_bed_capacity"]
			)
