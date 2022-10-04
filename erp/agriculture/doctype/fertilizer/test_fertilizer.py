# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestFertilizer(unittest.TestCase):
	def test_fertilizer_creation(self):
		self.assertEqual(capkpi.db.exists("Fertilizer", "Urea"), "Urea")
