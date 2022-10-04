import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "bank", force=1)

	if (
		capkpi.db.table_exists("Bank")
		and capkpi.db.table_exists("Bank Account")
		and capkpi.db.has_column("Bank Account", "swift_number")
	):
		try:
			capkpi.db.sql(
				"""
				UPDATE `tabBank` b, `tabBank Account` ba
				SET b.swift_number = ba.swift_number WHERE b.name = ba.bank
			"""
			)
		except Exception as e:
			capkpi.log_error(e, title="Patch Migration Failed")

	capkpi.reload_doc("accounts", "doctype", "bank_account")
	capkpi.reload_doc("accounts", "doctype", "payment_request")
