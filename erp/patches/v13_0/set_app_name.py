import capkpi


def execute():
	capkpi.reload_doctype("System Settings")
	settings = capkpi.get_doc("System Settings")
	settings.db_set("app_name", "ERP", commit=True)
