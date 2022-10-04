# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

from erp.education.api import get_grade

# test_records = capkpi.get_test_records('Assessment Result')


class TestAssessmentResult(unittest.TestCase):
	def test_grade(self):
		grade = get_grade("_Test Grading Scale", 80)
		self.assertEqual("A", grade)

		grade = get_grade("_Test Grading Scale", 70)
		self.assertEqual("B", grade)
