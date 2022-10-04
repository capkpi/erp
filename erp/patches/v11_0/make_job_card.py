# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

from erp.manufacturing.doctype.work_order.work_order import create_job_card


def execute():
	capkpi.reload_doc("manufacturing", "doctype", "work_order")
	capkpi.reload_doc("manufacturing", "doctype", "work_order_item")
	capkpi.reload_doc("manufacturing", "doctype", "job_card")
	capkpi.reload_doc("manufacturing", "doctype", "job_card_item")

	fieldname = capkpi.db.get_value(
		"DocField", {"fieldname": "work_order", "parent": "Timesheet"}, "fieldname"
	)
	if not fieldname:
		fieldname = capkpi.db.get_value(
			"DocField", {"fieldname": "production_order", "parent": "Timesheet"}, "fieldname"
		)
		if not fieldname:
			return

	for d in capkpi.get_all(
		"Timesheet", filters={fieldname: ["!=", ""], "docstatus": 0}, fields=[fieldname, "name"]
	):
		if d[fieldname]:
			doc = capkpi.get_doc("Work Order", d[fieldname])
			for row in doc.operations:
				create_job_card(doc, row, auto_create=True)
			capkpi.delete_doc("Timesheet", d.name)
