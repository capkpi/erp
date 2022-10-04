import capkpi


def execute():
	capkpi.reload_doc("stock", "doctype", "shipment")

	# update submitted status
	capkpi.db.sql(
		"""UPDATE `tabShipment`
					SET status = "Submitted"
					WHERE status = "Draft" AND docstatus = 1"""
	)

	# update cancelled status
	capkpi.db.sql(
		"""UPDATE `tabShipment`
					SET status = "Cancelled"
					WHERE status = "Draft" AND docstatus = 2"""
	)
