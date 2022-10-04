# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestQualityFeedback(unittest.TestCase):
	def test_quality_feedback(self):
		template = capkpi.get_doc(
			dict(
				doctype="Quality Feedback Template",
				template="Test Template",
				parameters=[dict(parameter="Test Parameter 1"), dict(parameter="Test Parameter 2")],
			)
		).insert()

		feedback = capkpi.get_doc(
			dict(
				doctype="Quality Feedback",
				template=template.name,
				document_type="User",
				document_name=capkpi.session.user,
			)
		).insert()

		self.assertEqual(template.parameters[0].parameter, feedback.parameters[0].parameter)

		feedback.delete()
		template.delete()
