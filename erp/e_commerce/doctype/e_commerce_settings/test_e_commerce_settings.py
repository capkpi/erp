# Copyright (c) 2022, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

from erp.e_commerce.doctype.e_commerce_settings.e_commerce_settings import (
	ShoppingCartSetupError,
)


class TestECommerceSettings(unittest.TestCase):
	def tearDown(self):
		capkpi.db.rollback()

	def test_tax_rule_validation(self):
		capkpi.db.sql("update `tabTax Rule` set use_for_shopping_cart = 0")

		cart_settings = capkpi.get_doc("E Commerce Settings")
		cart_settings.enabled = 1
		if not capkpi.db.get_value("Tax Rule", {"use_for_shopping_cart": 1}, "name"):
			self.assertRaises(ShoppingCartSetupError, cart_settings.validate_tax_rule)

		capkpi.db.sql("update `tabTax Rule` set use_for_shopping_cart = 1")

	def test_invalid_filter_fields(self):
		"Check if Item fields are blocked in E Commerce Settings filter fields."
		from capkpi.custom.doctype.custom_field.custom_field import create_custom_field

		setup_e_commerce_settings({"enable_field_filters": 1})

		create_custom_field(
			"Item",
			dict(owner="Administrator", fieldname="test_data", label="Test", fieldtype="Data"),
		)
		settings = capkpi.get_doc("E Commerce Settings")
		settings.append("filter_fields", {"fieldname": "test_data"})

		self.assertRaises(capkpi.ValidationError, settings.save)


def setup_e_commerce_settings(values_dict):
	"Accepts a dict of values that updates E Commerce Settings."
	if not values_dict:
		return

	doc = capkpi.get_doc("E Commerce Settings", "E Commerce Settings")
	doc.update(values_dict)
	doc.save()


test_dependencies = ["Tax Rule"]
