# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import add_months, nowdate

import erp
from erp.non_profit.doctype.member.member import create_member
from erp.non_profit.doctype.membership.membership import update_halted_razorpay_subscription


class TestMembership(unittest.TestCase):
	def setUp(self):
		plan = setup_membership()

		# make test member
		self.member_doc = create_member(
			capkpi._dict(
				{
					"fullname": "_Test_Member",
					"email": "_test_member_erp@example.com",
					"plan_id": plan.name,
					"subscription_id": "sub_DEX6xcJ1HSW4CR",
					"customer_id": "cust_C0WlbKhp3aLA7W",
					"subscription_status": "Active",
				}
			)
		)
		self.member_doc.make_customer_and_link()
		self.member = self.member_doc.name

	def test_auto_generate_invoice_and_payment_entry(self):
		entry = make_membership(self.member)

		# Naive test to see if at all invoice was generated and attached to member
		# In any case if details were missing, the invoicing would throw an error
		invoice = entry.generate_invoice(save=True)
		self.assertEqual(invoice.name, entry.invoice)

	def test_renew_within_30_days(self):
		# create a membership for two months
		# Should work fine
		make_membership(self.member, {"from_date": nowdate()})
		make_membership(self.member, {"from_date": add_months(nowdate(), 1)})

		from capkpi.utils.user import add_role

		add_role("test@example.com", "Non Profit Manager")
		capkpi.set_user("test@example.com")

		# create next membership with expiry not within 30 days
		self.assertRaises(
			capkpi.ValidationError,
			make_membership,
			self.member,
			{
				"from_date": add_months(nowdate(), 2),
			},
		)

		capkpi.set_user("Administrator")
		# create the same membership but as administrator
		make_membership(
			self.member,
			{
				"from_date": add_months(nowdate(), 2),
				"to_date": add_months(nowdate(), 3),
			},
		)

	def test_halted_memberships(self):
		make_membership(
			self.member, {"from_date": add_months(nowdate(), 2), "to_date": add_months(nowdate(), 3)}
		)

		self.assertEqual(capkpi.db.get_value("Member", self.member, "subscription_status"), "Active")
		payload = get_subscription_payload()
		update_halted_razorpay_subscription(data=payload)
		self.assertEqual(capkpi.db.get_value("Member", self.member, "subscription_status"), "Halted")

	def tearDown(self):
		capkpi.db.rollback()


def set_config(key, value):
	capkpi.db.set_value("Non Profit Settings", None, key, value)


def make_membership(member, payload={}):
	data = {
		"doctype": "Membership",
		"member": member,
		"membership_status": "Current",
		"membership_type": "_rzpy_test_milythm",
		"currency": "USD",
		"paid": 1,
		"from_date": nowdate(),
		"amount": 100,
	}
	data.update(payload)
	membership = capkpi.get_doc(data)
	membership.insert(ignore_permissions=True, ignore_if_duplicate=True)
	return membership


def create_item(item_code):
	if not capkpi.db.exists("Item", item_code):
		item = capkpi.new_doc("Item")
		item.item_code = item_code
		item.item_name = item_code
		item.stock_uom = "Nos"
		item.description = item_code
		item.item_group = "All Item Groups"
		item.is_stock_item = 0
		item.save()
	else:
		item = capkpi.get_doc("Item", item_code)
	return item


def setup_membership():
	# Get default company
	company = capkpi.get_doc("Company", erp.get_default_company())

	# update non profit settings
	settings = capkpi.get_doc("Non Profit Settings")
	# Enable razorpay
	settings.enable_razorpay_for_memberships = 1
	settings.billing_cycle = "Monthly"
	settings.billing_frequency = 24
	# Enable invoicing
	settings.allow_invoicing = 1
	settings.automate_membership_payment_entries = 1
	settings.company = company.name
	settings.donation_company = company.name
	settings.membership_payment_account = company.default_cash_account
	settings.membership_debit_account = company.default_receivable_account
	settings.flags.ignore_mandatory = True
	settings.save()

	# make test plan
	if not capkpi.db.exists("Membership Type", "_rzpy_test_milythm"):
		plan = capkpi.new_doc("Membership Type")
		plan.membership_type = "_rzpy_test_milythm"
		plan.amount = 100
		plan.razorpay_plan_id = "_rzpy_test_milythm"
		plan.linked_item = create_item("_Test Item for Non Profit Membership").name
		plan.insert()
	else:
		plan = capkpi.get_doc("Membership Type", "_rzpy_test_milythm")

	return plan


def get_subscription_payload():
	return {
		"entity": "event",
		"account_id": "acc_BFQ7uQEaa7j2z7",
		"event": "subscription.halted",
		"contains": ["subscription"],
		"payload": {
			"subscription": {
				"entity": {
					"id": "sub_DEX6xcJ1HSW4CR",
					"entity": "subscription",
					"plan_id": "_rzpy_test_milythm",
					"customer_id": "cust_C0WlbKhp3aLA7W",
					"status": "halted",
					"notes": {"Important": "Notes for Internal Reference"},
				}
			}
		},
	}
