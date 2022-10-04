# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestHealthcareServiceUnitType(unittest.TestCase):
	def test_item_creation(self):
		unit_type = get_unit_type()
		self.assertTrue(capkpi.db.exists("Item", unit_type.item))

		# check item disabled
		unit_type.disabled = 1
		unit_type.save()
		self.assertEqual(capkpi.db.get_value("Item", unit_type.item, "disabled"), 1)


def get_unit_type():
	if capkpi.db.exists("Healthcare Service Unit Type", "Inpatient Rooms"):
		return capkpi.get_doc("Healthcare Service Unit Type", "Inpatient Rooms")

	unit_type = capkpi.new_doc("Healthcare Service Unit Type")
	unit_type.service_unit_type = "Inpatient Rooms"
	unit_type.inpatient_occupancy = 1
	unit_type.is_billable = 1
	unit_type.item_code = "Inpatient Rooms"
	unit_type.item_group = "Services"
	unit_type.uom = "Hour"
	unit_type.no_of_hours = 1
	unit_type.rate = 4000
	unit_type.save()
	return unit_type
