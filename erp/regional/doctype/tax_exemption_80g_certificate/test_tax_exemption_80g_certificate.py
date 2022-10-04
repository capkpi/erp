# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import getdate

from erp.accounts.utils import get_fiscal_year
from erp.non_profit.doctype.donation.donation import create_razorpay_donation
from erp.non_profit.doctype.donation.test_donation import (
	create_donor,
	create_donor_type,
	create_mode_of_payment,
)
from erp.non_profit.doctype.member.member import create_member
from erp.non_profit.doctype.membership.test_membership import make_membership, setup_membership


class TestTaxExemption80GCertificate(unittest.TestCase):
	def setUp(self):
		capkpi.db.sql("delete from `tabTax Exemption 80G Certificate`")
		capkpi.db.sql("delete from `tabMembership`")
		create_donor_type()
		settings = capkpi.get_doc("Non Profit Settings")
		settings.company = "_Test Company"
		settings.donation_company = "_Test Company"
		settings.default_donor_type = "_Test Donor"
		settings.creation_user = "Administrator"
		settings.save()

		company = capkpi.get_doc("Company", "_Test Company")
		company.pan_details = "BBBTI3374C"
		company.company_80g_number = "NQ.CIT(E)I2018-19/DEL-IE28615-27062018/10087"
		company.with_effect_from = getdate()
		company.save()

	def test_duplicate_donation_certificate(self):
		donor = create_donor()
		create_mode_of_payment()
		payment = capkpi._dict(
			{"amount": 100, "method": "Debit Card", "id": "pay_MeXAmsgeKOhq7O"}  # rzp sends data in paise
		)
		donation = create_razorpay_donation(donor, payment)

		args = capkpi._dict({"recipient": "Donor", "donor": donor.name, "donation": donation.name})
		certificate = create_80g_certificate(args)
		certificate.insert()

		# check company details
		self.assertEqual(certificate.company_pan_number, "BBBTI3374C")
		self.assertEqual(certificate.company_80g_number, "NQ.CIT(E)I2018-19/DEL-IE28615-27062018/10087")

		# check donation details
		self.assertEqual(certificate.amount, donation.amount)

		duplicate_certificate = create_80g_certificate(args)
		# duplicate validation
		self.assertRaises(capkpi.ValidationError, duplicate_certificate.insert)

	def test_membership_80g_certificate(self):
		plan = setup_membership()

		# make test member
		member_doc = create_member(
			capkpi._dict(
				{"fullname": "_Test_Member", "email": "_test_member_erp@example.com", "plan_id": plan.name}
			)
		)
		member_doc.make_customer_and_link()
		member = member_doc.name

		membership = make_membership(member, {"from_date": getdate()})
		invoice = membership.generate_invoice(save=True)

		args = capkpi._dict(
			{
				"recipient": "Member",
				"member": member,
				"fiscal_year": get_fiscal_year(getdate(), as_dict=True).get("name"),
			}
		)
		certificate = create_80g_certificate(args)
		certificate.get_payments()
		certificate.insert()

		self.assertEqual(len(certificate.payments), 1)
		self.assertEqual(certificate.payments[0].amount, membership.amount)
		self.assertEqual(certificate.payments[0].invoice_id, invoice.name)


def create_80g_certificate(args):
	certificate = capkpi.get_doc(
		{
			"doctype": "Tax Exemption 80G Certificate",
			"recipient": args.recipient,
			"date": getdate(),
			"company": "_Test Company",
		}
	)

	certificate.update(args)

	return certificate
