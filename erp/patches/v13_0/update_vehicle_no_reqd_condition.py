import capkpi


def execute():
	capkpi.reload_doc("custom", "doctype", "custom_field", force=True)
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	if capkpi.db.exists("Custom Field", {"fieldname": "vehicle_no"}):
		capkpi.db.set_value("Custom Field", {"fieldname": "vehicle_no"}, "mandatory_depends_on", "")
