# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestDisease(unittest.TestCase):
	def test_treatment_period(self):
		disease = capkpi.get_doc("Disease", "Aphids")
		self.assertEqual(disease.treatment_period, 3)
