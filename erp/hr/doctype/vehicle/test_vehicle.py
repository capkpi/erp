# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import random_string

# test_records = capkpi.get_test_records('Vehicle')


class TestVehicle(unittest.TestCase):
	def test_make_vehicle(self):
		vehicle = capkpi.get_doc(
			{
				"doctype": "Vehicle",
				"license_plate": random_string(10).upper(),
				"make": "Maruti",
				"model": "PCM",
				"last_odometer": 5000,
				"acquisition_date": capkpi.utils.nowdate(),
				"location": "Mumbai",
				"chassis_no": "1234ABCD",
				"uom": "Litre",
				"vehicle_value": capkpi.utils.flt(500000),
			}
		)
		vehicle.insert()
