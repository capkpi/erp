# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import json
import unittest

import capkpi
from capkpi import _
from capkpi.utils import random_string

from erp.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
	get_charts_for_country,
)

test_ignore = ["Account", "Cost Center", "Payment Terms Template", "Salary Component", "Warehouse"]
test_dependencies = ["Fiscal Year"]
test_records = capkpi.get_test_records("Company")


class TestCompany(unittest.TestCase):
	def test_coa_based_on_existing_company(self):
		company = capkpi.new_doc("Company")
		company.company_name = "COA from Existing Company"
		company.abbr = "CFEC"
		company.default_currency = "INR"
		company.create_chart_of_accounts_based_on = "Existing Company"
		company.existing_company = "_Test Company"
		company.save()

		expected_results = {
			"Debtors - CFEC": {
				"account_type": "Receivable",
				"is_group": 0,
				"root_type": "Asset",
				"parent_account": "Accounts Receivable - CFEC",
			},
			"Cash - CFEC": {
				"account_type": "Cash",
				"is_group": 0,
				"root_type": "Asset",
				"parent_account": "Cash In Hand - CFEC",
			},
		}

		for account, acc_property in expected_results.items():
			acc = capkpi.get_doc("Account", account)
			for prop, val in acc_property.items():
				self.assertEqual(acc.get(prop), val)

		self.delete_mode_of_payment("COA from Existing Company")
		capkpi.delete_doc("Company", "COA from Existing Company")

	def test_coa_based_on_country_template(self):
		countries = ["Canada", "Germany", "France"]

		for country in countries:
			templates = get_charts_for_country(country)
			if len(templates) != 1 and "Standard" in templates:
				templates.remove("Standard")

			self.assertTrue(templates)

			for template in templates:
				try:
					company = capkpi.new_doc("Company")
					company.company_name = template
					company.abbr = random_string(3)
					company.default_currency = "USD"
					company.create_chart_of_accounts_based_on = "Standard Template"
					company.chart_of_accounts = template
					company.save()

					account_types = [
						"Cost of Goods Sold",
						"Depreciation",
						"Expenses Included In Valuation",
						"Fixed Asset",
						"Payable",
						"Receivable",
						"Stock Adjustment",
						"Stock Received But Not Billed",
						"Bank",
						"Cash",
						"Stock",
					]

					for account_type in account_types:
						filters = {"company": template, "account_type": account_type}
						if account_type in ["Bank", "Cash"]:
							filters["is_group"] = 1

						has_matching_accounts = capkpi.get_all("Account", filters)
						error_message = _("No Account matched these filters: {}").format(json.dumps(filters))

						self.assertTrue(has_matching_accounts, msg=error_message)
				finally:
					self.delete_mode_of_payment(template)
					capkpi.delete_doc("Company", template)

	def delete_mode_of_payment(self, company):
		capkpi.db.sql(
			""" delete from `tabMode of Payment Account`
			where company =%s """,
			(company),
		)

	def test_basic_tree(self, records=None):
		min_lft = 1
		max_rgt = capkpi.db.sql("select max(rgt) from `tabCompany`")[0][0]

		if not records:
			records = test_records[2:]

		for company in records:
			lft, rgt, parent_company = capkpi.db.get_value(
				"Company", company["company_name"], ["lft", "rgt", "parent_company"]
			)

			if parent_company:
				parent_lft, parent_rgt = capkpi.db.get_value("Company", parent_company, ["lft", "rgt"])
			else:
				# root
				parent_lft = min_lft - 1
				parent_rgt = max_rgt + 1

			self.assertTrue(lft)
			self.assertTrue(rgt)
			self.assertTrue(lft < rgt)
			self.assertTrue(parent_lft < parent_rgt)
			self.assertTrue(lft > parent_lft)
			self.assertTrue(rgt < parent_rgt)
			self.assertTrue(lft >= min_lft)
			self.assertTrue(rgt <= max_rgt)

	def get_no_of_children(self, company):
		def get_no_of_children(companies, no_of_children):
			children = []
			for company in companies:
				children += capkpi.db.sql_list(
					"""select name from `tabCompany`
				where ifnull(parent_company, '')=%s""",
					company or "",
				)

			if len(children):
				return get_no_of_children(children, no_of_children + len(children))
			else:
				return no_of_children

		return get_no_of_children([company], 0)

	def test_change_parent_company(self):
		child_company = capkpi.get_doc("Company", "_Test Company 5")

		# changing parent of company
		child_company.parent_company = "_Test Company 3"
		child_company.save()
		self.test_basic_tree()

		# move it back
		child_company.parent_company = "_Test Company 4"
		child_company.save()
		self.test_basic_tree()


def create_company_communication(doctype, docname):
	comm = capkpi.get_doc(
		{
			"doctype": "Communication",
			"communication_type": "Communication",
			"content": "Deduplication of Links",
			"communication_medium": "Email",
			"reference_doctype": doctype,
			"reference_name": docname,
		}
	)
	comm.insert()


def create_child_company():
	child_company = capkpi.db.exists("Company", "Test Company")
	if not child_company:
		child_company = capkpi.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Company",
				"abbr": "test_company",
				"default_currency": "INR",
			}
		)
		child_company.insert()
	else:
		child_company = capkpi.get_doc("Company", child_company)

	return child_company.name


def create_test_lead_in_company(company):
	lead = capkpi.db.exists("Lead", "Test Lead in new company")
	if not lead:
		lead = capkpi.get_doc(
			{"doctype": "Lead", "lead_name": "Test Lead in new company", "scompany": company}
		)
		lead.insert()
	else:
		lead = capkpi.get_doc("Lead", lead)
		lead.company = company
		lead.save()
	return lead.name
