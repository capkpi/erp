# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	if capkpi.db.table_exists("POS Closing Voucher"):
		if not capkpi.db.exists("DocType", "POS Closing Entry"):
			capkpi.rename_doc("DocType", "POS Closing Voucher", "POS Closing Entry", force=True)

		if not capkpi.db.exists("DocType", "POS Closing Entry Taxes"):
			capkpi.rename_doc("DocType", "POS Closing Voucher Taxes", "POS Closing Entry Taxes", force=True)

		if not capkpi.db.exists("DocType", "POS Closing Voucher Details"):
			capkpi.rename_doc(
				"DocType", "POS Closing Voucher Details", "POS Closing Entry Detail", force=True
			)

		capkpi.reload_doc("Accounts", "doctype", "POS Closing Entry")
		capkpi.reload_doc("Accounts", "doctype", "POS Closing Entry Taxes")
		capkpi.reload_doc("Accounts", "doctype", "POS Closing Entry Detail")

	if capkpi.db.exists("DocType", "POS Closing Voucher"):
		capkpi.delete_doc("DocType", "POS Closing Voucher")
		capkpi.delete_doc("DocType", "POS Closing Voucher Taxes")
		capkpi.delete_doc("DocType", "POS Closing Voucher Details")
		capkpi.delete_doc("DocType", "POS Closing Voucher Invoices")
