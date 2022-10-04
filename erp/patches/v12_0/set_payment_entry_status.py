import capkpi


def execute():
	capkpi.reload_doctype("Payment Entry")
	capkpi.db.sql(
		"""update `tabPayment Entry` set status = CASE
		WHEN docstatus = 1 THEN 'Submitted'
		WHEN docstatus = 2 THEN 'Cancelled'
		ELSE 'Draft'
		END;"""
	)
