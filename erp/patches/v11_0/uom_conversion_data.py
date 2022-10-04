import capkpi


def execute():
	from erp.setup.setup_wizard.operations.install_fixtures import add_uom_data

	capkpi.reload_doc("setup", "doctype", "UOM Conversion Factor")
	capkpi.reload_doc("setup", "doctype", "UOM")
	capkpi.reload_doc("stock", "doctype", "UOM Category")

	if not capkpi.db.a_row_exists("UOM Conversion Factor"):
		add_uom_data()
	else:
		# delete conversion data and insert again
		capkpi.db.sql("delete from `tabUOM Conversion Factor`")
		try:
			capkpi.delete_doc("UOM", "Hundredweight")
			capkpi.delete_doc("UOM", "Pound Cubic Yard")
		except capkpi.LinkExistsError:
			pass

		add_uom_data()
