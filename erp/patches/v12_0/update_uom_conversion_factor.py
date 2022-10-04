import capkpi


def execute():
	from erp.setup.setup_wizard.operations.install_fixtures import add_uom_data

	capkpi.reload_doc("setup", "doctype", "UOM Conversion Factor")
	capkpi.reload_doc("setup", "doctype", "UOM")
	capkpi.reload_doc("stock", "doctype", "UOM Category")

	add_uom_data()
