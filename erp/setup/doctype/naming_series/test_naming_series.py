# Copyright (c) 2022, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import capkpi
from capkpi.tests.utils import CapKPITestCase

from erp.setup.doctype.naming_series.naming_series import NamingSeries


class TestNamingSeries(CapKPITestCase):
	def setUp(self):
		self.ns: NamingSeries = capkpi.get_doc("Naming Series")

	def tearDown(self):
		capkpi.db.rollback()

	def test_naming_preview(self):
		self.ns.select_doc_for_series = "Sales Invoice"

		self.ns.naming_series_to_check = "AXBZ.####"
		serieses = self.ns.preview_series().split("\n")
		self.assertEqual(["AXBZ0001", "AXBZ0002", "AXBZ0003"], serieses)

		self.ns.naming_series_to_check = "AXBZ-.{currency}.-"
		serieses = self.ns.preview_series().split("\n")

	def test_get_transactions(self):

		naming_info = self.ns.get_transactions()
		self.assertIn("Sales Invoice", naming_info["transactions"])

		existing_naming_series = capkpi.get_meta("Sales Invoice").get_field("naming_series").options

		for series in existing_naming_series.split("\n"):
			self.assertIn(series, naming_info["prefixes"])
