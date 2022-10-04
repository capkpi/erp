import capkpi


def execute():
	capkpi.reload_doc("manufacturing", "doctype", "bom_operation")
	capkpi.reload_doc("manufacturing", "doctype", "work_order_operation")

	capkpi.db.sql(
		"""
        UPDATE
            `tabBOM Operation` bo
        SET
            bo.batch_size = 1
    """
	)
	capkpi.db.sql(
		"""
        UPDATE
            `tabWork Order Operation` wop
        SET
            wop.batch_size = 1
    """
	)
