import os

import capkpi
from capkpi import _


def execute():
	capkpi.reload_doc("email", "doctype", "email_template")
	capkpi.reload_doc("stock", "doctype", "delivery_settings")

	if not capkpi.db.exists("Email Template", _("Dispatch Notification")):
		base_path = capkpi.get_app_path("erp", "stock", "doctype")
		response = capkpi.read_file(
			os.path.join(base_path, "delivery_trip/dispatch_notification_template.html")
		)

		capkpi.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Dispatch Notification"),
				"response": response,
				"subject": _("Your order is out for delivery!"),
				"owner": capkpi.session.user,
			}
		).insert(ignore_permissions=True)

	delivery_settings = capkpi.get_doc("Delivery Settings")
	delivery_settings.dispatch_template = _("Dispatch Notification")
	delivery_settings.flags.ignore_links = True
	delivery_settings.save()
