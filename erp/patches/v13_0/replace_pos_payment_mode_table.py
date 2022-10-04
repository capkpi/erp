# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "pos_payment_method")
	pos_profiles = capkpi.get_all("POS Profile")

	for pos_profile in pos_profiles:
		payments = capkpi.db.sql(
			"""
			select idx, parentfield, parenttype, parent, mode_of_payment, `default` from `tabSales Invoice Payment` where parent=%s
		""",
			pos_profile.name,
			as_dict=1,
		)
		if payments:
			for payment_mode in payments:
				pos_payment_method = capkpi.new_doc("POS Payment Method")
				pos_payment_method.idx = payment_mode.idx
				pos_payment_method.default = payment_mode.default
				pos_payment_method.mode_of_payment = payment_mode.mode_of_payment
				pos_payment_method.parent = payment_mode.parent
				pos_payment_method.parentfield = payment_mode.parentfield
				pos_payment_method.parenttype = payment_mode.parenttype
				pos_payment_method.db_insert()

		capkpi.db.sql("""delete from `tabSales Invoice Payment` where parent=%s""", pos_profile.name)
