import capkpi
from capkpi.model.utils.rename_field import rename_field


def execute():
	capkpi.reload_doc("stock", "doctype", "item")
	capkpi.reload_doc("stock", "doctype", "stock_settings")
	capkpi.reload_doc("accounts", "doctype", "accounts_settings")

	rename_field("Stock Settings", "tolerance", "over_delivery_receipt_allowance")
	rename_field("Item", "tolerance", "over_delivery_receipt_allowance")

	qty_allowance = capkpi.db.get_single_value("Stock Settings", "over_delivery_receipt_allowance")
	capkpi.db.set_value("Accounts Settings", None, "over_delivery_receipt_allowance", qty_allowance)

	capkpi.db.sql("update tabItem set over_billing_allowance=over_delivery_receipt_allowance")
