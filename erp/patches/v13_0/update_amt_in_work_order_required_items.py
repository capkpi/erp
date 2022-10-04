import capkpi


def execute():
	"""Correct amount in child table of required items table."""

	capkpi.reload_doc("manufacturing", "doctype", "work_order")
	capkpi.reload_doc("manufacturing", "doctype", "work_order_item")

	capkpi.db.sql("""UPDATE `tabWork Order Item` SET amount = rate * required_qty""")
