# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

from erp.hotels.doctype.hotel_room_reservation.hotel_room_reservation import (
	HotelRoomPricingNotSetError,
	HotelRoomUnavailableError,
)

test_dependencies = ["Hotel Room Package", "Hotel Room Pricing", "Hotel Room"]


class TestHotelRoomReservation(unittest.TestCase):
	def setUp(self):
		capkpi.db.sql("delete from `tabHotel Room Reservation`")
		capkpi.db.sql("delete from `tabHotel Room Reservation Item`")

	def test_reservation(self):
		reservation = make_reservation(
			from_date="2017-01-01", to_date="2017-01-03", items=[dict(item="Basic Room with Dinner", qty=2)]
		)
		reservation.insert()
		self.assertEqual(reservation.net_total, 48000)

	def test_price_not_set(self):
		reservation = make_reservation(
			from_date="2016-01-01", to_date="2016-01-03", items=[dict(item="Basic Room with Dinner", qty=2)]
		)
		self.assertRaises(HotelRoomPricingNotSetError, reservation.insert)

	def test_room_unavailable(self):
		reservation = make_reservation(
			from_date="2017-01-01",
			to_date="2017-01-03",
			items=[
				dict(item="Basic Room with Dinner", qty=2),
			],
		)
		reservation.insert()

		reservation = make_reservation(
			from_date="2017-01-01",
			to_date="2017-01-03",
			items=[
				dict(item="Basic Room with Dinner", qty=20),
			],
		)
		self.assertRaises(HotelRoomUnavailableError, reservation.insert)


def make_reservation(**kwargs):
	kwargs["doctype"] = "Hotel Room Reservation"
	if not "guest_name" in kwargs:
		kwargs["guest_name"] = "Test Guest"
	doc = capkpi.get_doc(kwargs)
	return doc
