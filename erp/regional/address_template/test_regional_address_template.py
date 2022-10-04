from unittest import TestCase

import capkpi

from erp.regional.address_template.setup import get_address_templates, update_address_template


def ensure_country(country):
	if capkpi.db.exists("Country", country):
		return capkpi.get_doc("Country", country)
	else:
		c = capkpi.get_doc({"doctype": "Country", "country_name": country})
		c.insert()
		return c


class TestRegionalAddressTemplate(TestCase):
	def test_get_address_templates(self):
		"""Get the countries and paths from the templates directory."""
		templates = get_address_templates()
		self.assertIsInstance(templates, list)
		self.assertIsInstance(templates[0], tuple)

	def test_create_address_template(self):
		"""Create a new Address Template."""
		country = ensure_country("Germany")
		update_address_template(country.name, "TEST")
		doc = capkpi.get_doc("Address Template", country.name)
		self.assertEqual(doc.template, "TEST")

	def test_update_address_template(self):
		"""Update an existing Address Template."""
		country = ensure_country("Germany")
		if not capkpi.db.exists("Address Template", country.name):
			template = capkpi.get_doc(
				{"doctype": "Address Template", "country": country.name, "template": "EXISTING"}
			).insert()

		update_address_template(country.name, "NEW")
		doc = capkpi.get_doc("Address Template", country.name)
		self.assertEqual(doc.template, "NEW")
