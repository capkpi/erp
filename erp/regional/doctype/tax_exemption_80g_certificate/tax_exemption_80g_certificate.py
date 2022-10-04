# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.contacts.doctype.address.address import get_company_address
from capkpi.model.document import Document
from capkpi.utils import flt, get_link_to_form

from erp.accounts.utils import get_fiscal_year


class TaxExemption80GCertificate(Document):
	def validate(self):
		self.validate_duplicates()
		self.validate_company_details()
		self.set_company_address()
		self.calculate_total()
		self.set_title()

	def validate_duplicates(self):
		if self.recipient == "Donor":
			certificate = capkpi.db.exists(
				self.doctype, {"donation": self.donation, "name": ("!=", self.name)}
			)
			if certificate:
				capkpi.throw(
					_("An 80G Certificate {0} already exists for the donation {1}").format(
						get_link_to_form(self.doctype, certificate), capkpi.bold(self.donation)
					),
					title=_("Duplicate Certificate"),
				)

	def validate_company_details(self):
		fields = ["company_80g_number", "with_effect_from", "pan_details"]
		company_details = capkpi.db.get_value("Company", self.company, fields, as_dict=True)
		if not company_details.company_80g_number:
			capkpi.throw(
				_("Please set the {0} for company {1}").format(
					capkpi.bold("80G Number"), get_link_to_form("Company", self.company)
				)
			)

		if not company_details.pan_details:
			capkpi.throw(
				_("Please set the {0} for company {1}").format(
					capkpi.bold("PAN Number"), get_link_to_form("Company", self.company)
				)
			)

	@capkpi.whitelist()
	def set_company_address(self):
		address = get_company_address(self.company)
		self.company_address = address.company_address
		self.company_address_display = address.company_address_display

	def calculate_total(self):
		if self.recipient == "Donor":
			return

		total = 0
		for entry in self.payments:
			total += flt(entry.amount)
		self.total = total

	def set_title(self):
		if self.recipient == "Member":
			self.title = self.member_name
		else:
			self.title = self.donor_name

	@capkpi.whitelist()
	def get_payments(self):
		if not self.member:
			capkpi.throw(_("Please select a Member first."))

		fiscal_year = get_fiscal_year(fiscal_year=self.fiscal_year, as_dict=True)

		memberships = capkpi.db.get_all(
			"Membership",
			{
				"member": self.member,
				"from_date": ["between", (fiscal_year.year_start_date, fiscal_year.year_end_date)],
				"membership_status": ("!=", "Cancelled"),
			},
			["from_date", "amount", "name", "invoice", "payment_id"],
			order_by="from_date",
		)

		if not memberships:
			capkpi.msgprint(_("No Membership Payments found against the Member {0}").format(self.member))

		total = 0
		self.payments = []

		for doc in memberships:
			self.append(
				"payments",
				{
					"date": doc.from_date,
					"amount": doc.amount,
					"invoice_id": doc.invoice,
					"payment_id": doc.payment_id,
					"membership": doc.name,
				},
			)
			total += flt(doc.amount)

		self.total = total
