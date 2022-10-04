import os

import capkpi
from capkpi import _


def execute():
	capkpi.reload_doc("email", "doctype", "email_template")

	if not capkpi.db.exists("Email Template", _("Leave Approval Notification")):
		base_path = capkpi.get_app_path("erp", "hr", "doctype")
		response = capkpi.read_file(
			os.path.join(base_path, "leave_application/leave_application_email_template.html")
		)
		capkpi.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Leave Approval Notification"),
				"response": response,
				"subject": _("Leave Approval Notification"),
				"owner": capkpi.session.user,
			}
		).insert(ignore_permissions=True)

	if not capkpi.db.exists("Email Template", _("Leave Status Notification")):
		base_path = capkpi.get_app_path("erp", "hr", "doctype")
		response = capkpi.read_file(
			os.path.join(base_path, "leave_application/leave_application_email_template.html")
		)
		capkpi.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Leave Status Notification"),
				"response": response,
				"subject": _("Leave Status Notification"),
				"owner": capkpi.session.user,
			}
		).insert(ignore_permissions=True)
