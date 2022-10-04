import capkpi


def execute():
	capkpi.reload_doc("hr", "doctype", "hr_settings")
	capkpi.db.set_value("HR Settings", None, "payroll_based_on", "Leave")
