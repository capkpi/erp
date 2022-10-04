import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "pos_closing_entry")

	capkpi.db.sql("update `tabPOS Closing Entry` set `status` = 'Failed' where `status` = 'Queued'")
