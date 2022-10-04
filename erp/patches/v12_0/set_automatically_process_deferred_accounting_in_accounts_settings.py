import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "accounts_settings")

	capkpi.db.set_value(
		"Accounts Settings", None, "automatically_process_deferred_accounting_entry", 1
	)
