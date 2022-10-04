# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import add_days, date_diff, flt


class HotelRoomUnavailableError(capkpi.ValidationError):
	pass


class HotelRoomPricingNotSetError(capkpi.ValidationError):
	pass


class HotelRoomReservation(Document):
	def validate(self):
		self.total_rooms = {}
		self.set_rates()
		self.validate_availability()

	def validate_availability(self):
		for i in range(date_diff(self.to_date, self.from_date)):
			day = add_days(self.from_date, i)
			self.rooms_booked = {}

			for d in self.items:
				if not d.item in self.rooms_booked:
					self.rooms_booked[d.item] = 0

				room_type = capkpi.db.get_value("Hotel Room Package", d.item, "hotel_room_type")
				rooms_booked = (
					get_rooms_booked(room_type, day, exclude_reservation=self.name)
					+ d.qty
					+ self.rooms_booked.get(d.item)
				)
				total_rooms = self.get_total_rooms(d.item)
				if total_rooms < rooms_booked:
					capkpi.throw(
						_("Hotel Rooms of type {0} are unavailable on {1}").format(
							d.item, capkpi.format(day, dict(fieldtype="Date"))
						),
						exc=HotelRoomUnavailableError,
					)

				self.rooms_booked[d.item] += rooms_booked

	def get_total_rooms(self, item):
		if not item in self.total_rooms:
			self.total_rooms[item] = (
				capkpi.db.sql(
					"""
				select count(*)
				from
					`tabHotel Room Package` package
				inner join
					`tabHotel Room` room on package.hotel_room_type = room.hotel_room_type
				where
					package.item = %s""",
					item,
				)[0][0]
				or 0
			)

		return self.total_rooms[item]

	def set_rates(self):
		self.net_total = 0
		for d in self.items:
			net_rate = 0.0
			for i in range(date_diff(self.to_date, self.from_date)):
				day = add_days(self.from_date, i)
				if not d.item:
					continue
				day_rate = capkpi.db.sql(
					"""
					select
						item.rate
					from
						`tabHotel Room Pricing Item` item,
						`tabHotel Room Pricing` pricing
					where
						item.parent = pricing.name
						and item.item = %s
						and %s between pricing.from_date
							and pricing.to_date""",
					(d.item, day),
				)

				if day_rate:
					net_rate += day_rate[0][0]
				else:
					capkpi.throw(
						_("Please set Hotel Room Rate on {}").format(capkpi.format(day, dict(fieldtype="Date"))),
						exc=HotelRoomPricingNotSetError,
					)
			d.rate = net_rate
			d.amount = net_rate * flt(d.qty)
			self.net_total += d.amount


@capkpi.whitelist()
def get_room_rate(hotel_room_reservation):
	"""Calculate rate for each day as it may belong to different Hotel Room Pricing Item"""
	doc = capkpi.get_doc(json.loads(hotel_room_reservation))
	doc.set_rates()
	return doc.as_dict()


def get_rooms_booked(room_type, day, exclude_reservation=None):
	exclude_condition = ""
	if exclude_reservation:
		exclude_condition = "and reservation.name != {0}".format(capkpi.db.escape(exclude_reservation))

	return (
		capkpi.db.sql(
			"""
		select sum(item.qty)
		from
			`tabHotel Room Package` room_package,
			`tabHotel Room Reservation Item` item,
			`tabHotel Room Reservation` reservation
		where
			item.parent = reservation.name
			and room_package.item = item.item
			and room_package.hotel_room_type = %s
			and reservation.docstatus = 1
			{exclude_condition}
			and %s between reservation.from_date
				and reservation.to_date""".format(
				exclude_condition=exclude_condition
			),
			(room_type, day),
		)[0][0]
		or 0
	)
