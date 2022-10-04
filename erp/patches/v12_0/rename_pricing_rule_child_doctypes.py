# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

doctypes = {
	"Price Discount Slab": "Promotional Scheme Price Discount",
	"Product Discount Slab": "Promotional Scheme Product Discount",
	"Apply Rule On Item Code": "Pricing Rule Item Code",
	"Apply Rule On Item Group": "Pricing Rule Item Group",
	"Apply Rule On Brand": "Pricing Rule Brand",
}


def execute():
	for old_doc, new_doc in doctypes.items():
		if not capkpi.db.table_exists(new_doc) and capkpi.db.table_exists(old_doc):
			capkpi.rename_doc("DocType", old_doc, new_doc)
			capkpi.reload_doc("accounts", "doctype", capkpi.scrub(new_doc))
			capkpi.delete_doc("DocType", old_doc)
