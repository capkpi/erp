import capkpi


def execute():
	capkpi.rename_doc("DocType", "Account Type", "Bank Account Type", force=True)
	capkpi.rename_doc("DocType", "Account Subtype", "Bank Account Subtype", force=True)
	capkpi.reload_doc("accounts", "doctype", "bank_account")
