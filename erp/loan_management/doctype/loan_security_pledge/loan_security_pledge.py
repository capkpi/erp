# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import cint, now_datetime

from erp.loan_management.doctype.loan_security_price.loan_security_price import (
	get_loan_security_price,
)
from erp.loan_management.doctype.loan_security_shortfall.loan_security_shortfall import (
	update_shortfall_status,
)


class LoanSecurityPledge(Document):
	def validate(self):
		self.set_pledge_amount()
		self.validate_duplicate_securities()
		self.validate_loan_security_type()

	def on_submit(self):
		if self.loan:
			self.db_set("status", "Pledged")
			self.db_set("pledge_time", now_datetime())
			update_shortfall_status(self.loan, self.total_security_value)
			update_loan(self.loan, self.maximum_loan_value)

	def on_cancel(self):
		if self.loan:
			self.db_set("status", "Cancelled")
			self.db_set("pledge_time", None)
			update_loan(self.loan, self.maximum_loan_value, cancel=1)

	def validate_duplicate_securities(self):
		security_list = []
		for security in self.securities:
			if security.loan_security not in security_list:
				security_list.append(security.loan_security)
			else:
				capkpi.throw(
					_("Loan Security {0} added multiple times").format(capkpi.bold(security.loan_security))
				)

	def validate_loan_security_type(self):
		existing_pledge = ""

		if self.loan:
			existing_pledge = capkpi.db.get_value(
				"Loan Security Pledge", {"loan": self.loan, "docstatus": 1}, ["name"]
			)

		if existing_pledge:
			loan_security_type = capkpi.db.get_value(
				"Pledge", {"parent": existing_pledge}, ["loan_security_type"]
			)
		else:
			loan_security_type = self.securities[0].loan_security_type

		ltv_ratio_map = capkpi._dict(
			capkpi.get_all("Loan Security Type", fields=["name", "loan_to_value_ratio"], as_list=1)
		)

		ltv_ratio = ltv_ratio_map.get(loan_security_type)

		for security in self.securities:
			if ltv_ratio_map.get(security.loan_security_type) != ltv_ratio:
				capkpi.throw(_("Loan Securities with different LTV ratio cannot be pledged against one loan"))

	def set_pledge_amount(self):
		total_security_value = 0
		maximum_loan_value = 0

		for pledge in self.securities:

			if not pledge.qty and not pledge.amount:
				capkpi.throw(_("Qty or Amount is mandatory for loan security!"))

			if not (self.loan_application and pledge.loan_security_price):
				pledge.loan_security_price = get_loan_security_price(pledge.loan_security)

			if not pledge.qty:
				pledge.qty = cint(pledge.amount / pledge.loan_security_price)

			pledge.amount = pledge.qty * pledge.loan_security_price
			pledge.post_haircut_amount = cint(pledge.amount - (pledge.amount * pledge.haircut / 100))

			total_security_value += pledge.amount
			maximum_loan_value += pledge.post_haircut_amount

		self.total_security_value = total_security_value
		self.maximum_loan_value = maximum_loan_value


def update_loan(loan, maximum_value_against_pledge, cancel=0):
	maximum_loan_value = capkpi.db.get_value("Loan", {"name": loan}, ["maximum_loan_amount"])

	if cancel:
		capkpi.db.sql(
			""" UPDATE `tabLoan` SET maximum_loan_amount=%s
			WHERE name=%s""",
			(maximum_loan_value - maximum_value_against_pledge, loan),
		)
	else:
		capkpi.db.sql(
			""" UPDATE `tabLoan` SET maximum_loan_amount=%s, is_secured_loan=1
			WHERE name=%s""",
			(maximum_loan_value + maximum_value_against_pledge, loan),
		)
