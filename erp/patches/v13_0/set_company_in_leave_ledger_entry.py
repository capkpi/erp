import capkpi


def execute():
	capkpi.reload_doc("HR", "doctype", "Leave Allocation")
	capkpi.reload_doc("HR", "doctype", "Leave Ledger Entry")
	capkpi.db.sql(
		"""update `tabLeave Ledger Entry` as lle set company = (select company from `tabEmployee` where employee = lle.employee)"""
	)
	capkpi.db.sql(
		"""update `tabLeave Allocation` as la set company = (select company from `tabEmployee` where employee = la.employee)"""
	)
