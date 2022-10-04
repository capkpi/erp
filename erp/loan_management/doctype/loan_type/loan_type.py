# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class LoanType(Document):
	def validate(self):
		self.validate_accounts()

	def validate_accounts(self):
		for fieldname in [
			"payment_account",
			"loan_account",
			"interest_income_account",
			"penalty_income_account",
		]:
			company = capkpi.get_value("Account", self.get(fieldname), "company")

			if company and company != self.company:
				capkpi.throw(
					_("Account {0} does not belong to company {1}").format(
						capkpi.bold(self.get(fieldname)), capkpi.bold(self.company)
					)
				)

		if self.get("loan_account") == self.get("payment_account"):
			capkpi.throw(_("Loan Account and Payment Account cannot be same"))
