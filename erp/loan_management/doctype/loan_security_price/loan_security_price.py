# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import get_datetime


class LoanSecurityPrice(Document):
	def validate(self):
		self.validate_dates()

	def validate_dates(self):

		if self.valid_from > self.valid_upto:
			capkpi.throw(_("Valid From Time must be lesser than Valid Upto Time."))

		existing_loan_security = capkpi.db.sql(
			""" SELECT name from `tabLoan Security Price`
			WHERE loan_security = %s AND name != %s AND (valid_from BETWEEN %s and %s OR valid_upto BETWEEN %s and %s) """,
			(
				self.loan_security,
				self.name,
				self.valid_from,
				self.valid_upto,
				self.valid_from,
				self.valid_upto,
			),
		)

		if existing_loan_security:
			capkpi.throw(_("Loan Security Price overlapping with {0}").format(existing_loan_security[0][0]))


@capkpi.whitelist()
def get_loan_security_price(loan_security, valid_time=None):
	if not valid_time:
		valid_time = get_datetime()

	loan_security_price = capkpi.db.get_value(
		"Loan Security Price",
		{
			"loan_security": loan_security,
			"valid_from": ("<=", valid_time),
			"valid_upto": (">=", valid_time),
		},
		"loan_security_price",
	)

	if not loan_security_price:
		capkpi.throw(_("No valid Loan Security Price found for {0}").format(capkpi.bold(loan_security)))
	else:
		return loan_security_price
