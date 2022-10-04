# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

from erp.accounts.doctype.promotional_scheme.promotional_scheme import TransactionExists
from erp.selling.doctype.sales_order.test_sales_order import make_sales_order


class TestPromotionalScheme(unittest.TestCase):
	def setUp(self):
		if capkpi.db.exists("Promotional Scheme", "_Test Scheme"):
			capkpi.delete_doc("Promotional Scheme", "_Test Scheme")

	def test_promotional_scheme(self):
		ps = make_promotional_scheme(applicable_for="Customer", customer="_Test Customer")
		price_rules = capkpi.get_all(
			"Pricing Rule",
			fields=["promotional_scheme_id", "name", "creation"],
			filters={"promotional_scheme": ps.name},
		)
		self.assertTrue(len(price_rules), 1)
		price_doc_details = capkpi.db.get_value(
			"Pricing Rule", price_rules[0].name, ["customer", "min_qty", "discount_percentage"], as_dict=1
		)
		self.assertTrue(price_doc_details.customer, "_Test Customer")
		self.assertTrue(price_doc_details.min_qty, 4)
		self.assertTrue(price_doc_details.discount_percentage, 20)

		ps.price_discount_slabs[0].min_qty = 6
		ps.append("customer", {"customer": "_Test Customer 2"})
		ps.save()
		price_rules = capkpi.get_all(
			"Pricing Rule",
			fields=["promotional_scheme_id", "name"],
			filters={"promotional_scheme": ps.name},
		)
		self.assertTrue(len(price_rules), 2)

		price_doc_details = capkpi.db.get_value(
			"Pricing Rule", price_rules[1].name, ["customer", "min_qty", "discount_percentage"], as_dict=1
		)
		self.assertTrue(price_doc_details.customer, "_Test Customer 2")
		self.assertTrue(price_doc_details.min_qty, 6)
		self.assertTrue(price_doc_details.discount_percentage, 20)

		price_doc_details = capkpi.db.get_value(
			"Pricing Rule", price_rules[0].name, ["customer", "min_qty", "discount_percentage"], as_dict=1
		)
		self.assertTrue(price_doc_details.customer, "_Test Customer")
		self.assertTrue(price_doc_details.min_qty, 6)

		capkpi.delete_doc("Promotional Scheme", ps.name)
		price_rules = capkpi.get_all(
			"Pricing Rule",
			fields=["promotional_scheme_id", "name"],
			filters={"promotional_scheme": ps.name},
		)
		self.assertEqual(price_rules, [])

	def test_promotional_scheme_without_applicable_for(self):
		ps = make_promotional_scheme()
		price_rules = capkpi.get_all("Pricing Rule", filters={"promotional_scheme": ps.name})

		self.assertTrue(len(price_rules), 1)
		capkpi.delete_doc("Promotional Scheme", ps.name)

		price_rules = capkpi.get_all("Pricing Rule", filters={"promotional_scheme": ps.name})
		self.assertEqual(price_rules, [])

	def test_change_applicable_for_in_promotional_scheme(self):
		ps = make_promotional_scheme()
		price_rules = capkpi.get_all("Pricing Rule", filters={"promotional_scheme": ps.name})
		self.assertTrue(len(price_rules), 1)

		so = make_sales_order(qty=5, currency="USD", do_not_save=True)
		so.set_missing_values()
		so.save()
		self.assertEqual(price_rules[0].name, so.pricing_rules[0].pricing_rule)

		ps.applicable_for = "Customer"
		ps.append("customer", {"customer": "_Test Customer"})

		self.assertRaises(TransactionExists, ps.save)

		capkpi.delete_doc("Sales Order", so.name)
		capkpi.delete_doc("Promotional Scheme", ps.name)
		price_rules = capkpi.get_all("Pricing Rule", filters={"promotional_scheme": ps.name})
		self.assertEqual(price_rules, [])


def make_promotional_scheme(**args):
	args = capkpi._dict(args)

	ps = capkpi.new_doc("Promotional Scheme")
	ps.name = "_Test Scheme"
	ps.append("items", {"item_code": "_Test Item"})

	ps.selling = 1
	ps.append(
		"price_discount_slabs",
		{
			"min_qty": 4,
			"validate_applied_rule": 0,
			"discount_percentage": 20,
			"rule_description": "Test",
		},
	)

	ps.company = "_Test Company"
	if args.applicable_for:
		ps.applicable_for = args.applicable_for
		ps.append(
			capkpi.scrub(args.applicable_for),
			{capkpi.scrub(args.applicable_for): args.get(capkpi.scrub(args.applicable_for))},
		)

	ps.save()

	return ps
