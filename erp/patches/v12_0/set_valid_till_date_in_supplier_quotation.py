import capkpi


def execute():
	capkpi.reload_doc("buying", "doctype", "supplier_quotation")
	capkpi.db.sql(
		"""UPDATE `tabSupplier Quotation`
		SET valid_till = DATE_ADD(transaction_date , INTERVAL 1 MONTH)
		WHERE docstatus < 2"""
	)
