import unittest

import capkpi

import erp


@erp.allow_regional
def test_method():
	return "original"


class TestInit(unittest.TestCase):
	def test_regional_overrides(self):
		capkpi.flags.country = "India"
		self.assertEqual(test_method(), "overridden")

		capkpi.flags.country = "Maldives"
		self.assertEqual(test_method(), "original")

		capkpi.flags.country = "France"
		self.assertEqual(test_method(), "overridden")
