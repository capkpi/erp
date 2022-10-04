# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import scrub
from capkpi.model.utils.rename_field import rename_field


def execute():
	for doctype in ("Salary Component", "Salary Detail"):
		if "depends_on_lwp" in capkpi.db.get_table_columns(doctype):
			capkpi.reload_doc("Payroll", "doctype", scrub(doctype))
			rename_field(doctype, "depends_on_lwp", "depends_on_payment_days")
