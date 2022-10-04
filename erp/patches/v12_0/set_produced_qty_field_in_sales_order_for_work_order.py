import capkpi

from erp.selling.doctype.sales_order.sales_order import update_produced_qty_in_so_item


def execute():
	capkpi.reload_doctype("Sales Order Item")
	capkpi.reload_doctype("Sales Order")

	for d in capkpi.get_all(
		"Work Order",
		fields=["sales_order", "sales_order_item"],
		filters={"sales_order": ("!=", ""), "sales_order_item": ("!=", "")},
	):

		# update produced qty in sales order
		update_produced_qty_in_so_item(d.sales_order, d.sales_order_item)
