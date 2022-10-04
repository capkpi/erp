# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "Payment Schedule")
	if capkpi.db.count("Payment Schedule"):
		capkpi.db.sql(
			"""
			UPDATE
				`tabPayment Schedule` ps
			SET
				ps.outstanding = (ps.payment_amount - ps.paid_amount)
		"""
		)
