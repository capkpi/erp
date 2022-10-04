import capkpi


def execute():

	doctype = "Stock Reconciliation Item"

	if not capkpi.db.has_column(doctype, "current_serial_no"):
		# nothing to fix if column doesn't exist
		return

	sr_item = capkpi.qb.DocType(doctype)

	(
		capkpi.qb.update(sr_item).set(sr_item.current_serial_no, None).where(sr_item.current_qty == 0)
	).run()
