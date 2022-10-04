# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document
from capkpi.utils import get_datetime

from erp.loan_management.doctype.loan_security_shortfall.loan_security_shortfall import (
	check_for_ltv_shortfall,
)


class ProcessLoanSecurityShortfall(Document):
	def onload(self):
		self.set_onload("update_time", get_datetime())

	def on_submit(self):
		check_for_ltv_shortfall(self.name)


def create_process_loan_security_shortfall():
	if check_for_secured_loans():
		process = capkpi.new_doc("Process Loan Security Shortfall")
		process.update_time = get_datetime()
		process.submit()


def check_for_secured_loans():
	return capkpi.db.count("Loan", {"docstatus": 1, "is_secured_loan": 1})
