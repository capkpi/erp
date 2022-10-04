# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_stock_entry_types()

	company = capkpi.db.get_value("Company", {"country": "India"}, "name")
	if company:
		add_gst_hsn_code_field()


def create_stock_entry_types():
	capkpi.reload_doc("stock", "doctype", "stock_entry_type")
	capkpi.reload_doc("stock", "doctype", "stock_entry")

	for purpose in [
		"Material Issue",
		"Material Receipt",
		"Material Transfer",
		"Material Transfer for Manufacture",
		"Material Consumption for Manufacture",
		"Manufacture",
		"Repack",
		"Send to Subcontractor",
	]:

		ste_type = capkpi.get_doc({"doctype": "Stock Entry Type", "name": purpose, "purpose": purpose})

		try:
			ste_type.insert()
		except capkpi.DuplicateEntryError:
			pass

	capkpi.db.sql(
		" UPDATE `tabStock Entry` set purpose = 'Send to Subcontractor' where purpose = 'Subcontract'"
	)
	capkpi.db.sql(" UPDATE `tabStock Entry` set stock_entry_type = purpose ")


def add_gst_hsn_code_field():
	custom_fields = {
		"Stock Entry Detail": [
			dict(
				fieldname="gst_hsn_code",
				label="HSN/SAC",
				fieldtype="Data",
				fetch_from="item_code.gst_hsn_code",
				insert_after="description",
				allow_on_submit=1,
				print_hide=0,
			)
		]
	}

	create_custom_fields(custom_fields, ignore_validate=capkpi.flags.in_patch, update=True)

	capkpi.db.sql(
		""" update `tabStock Entry Detail`, `tabItem`
		SET
			`tabStock Entry Detail`.gst_hsn_code = `tabItem`.gst_hsn_code
		Where
			`tabItem`.name = `tabStock Entry Detail`.item_code and `tabItem`.gst_hsn_code is not null
	"""
	)
