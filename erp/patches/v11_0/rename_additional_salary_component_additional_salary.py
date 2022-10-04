import capkpi

# this patch should have been included with this PR https://github.com/capkpi/erp/pull/14302


def execute():
	if capkpi.db.table_exists("Additional Salary Component"):
		if not capkpi.db.table_exists("Additional Salary"):
			capkpi.rename_doc("DocType", "Additional Salary Component", "Additional Salary")

		capkpi.delete_doc("DocType", "Additional Salary Component")
