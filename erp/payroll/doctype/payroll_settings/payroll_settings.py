# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.custom.doctype.property_setter.property_setter import make_property_setter
from capkpi.model.document import Document
from capkpi.utils import cint


class PayrollSettings(Document):
	def validate(self):
		self.validate_password_policy()

		if not self.daily_wages_fraction_for_half_day:
			self.daily_wages_fraction_for_half_day = 0.5

	def validate_password_policy(self):
		if self.email_salary_slip_to_employee and self.encrypt_salary_slips_in_emails:
			if not self.password_policy:
				capkpi.throw(_("Password policy for Salary Slips is not set"))

	def on_update(self):
		self.toggle_rounded_total()
		capkpi.clear_cache()

	def toggle_rounded_total(self):
		self.disable_rounded_total = cint(self.disable_rounded_total)
		make_property_setter(
			"Salary Slip",
			"rounded_total",
			"hidden",
			self.disable_rounded_total,
			"Check",
			validate_fields_for_doctype=False,
		)
		make_property_setter(
			"Salary Slip",
			"rounded_total",
			"print_hide",
			self.disable_rounded_total,
			"Check",
			validate_fields_for_doctype=False,
		)