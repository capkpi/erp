import capkpi


def execute():
	capkpi.reload_doctype("Employee")
	capkpi.db.sql("update tabEmployee set first_name = employee_name")

	# update holiday list
	capkpi.reload_doctype("Holiday List")
	for holiday_list in capkpi.get_all("Holiday List"):
		holiday_list = capkpi.get_doc("Holiday List", holiday_list.name)
		holiday_list.db_set("total_holidays", len(holiday_list.holidays), update_modified=False)
