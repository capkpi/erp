import capkpi
from capkpi import _


def execute():
	"""assign lft and rgt appropriately"""
	if "Healthcare" not in capkpi.get_active_domains():
		return

	capkpi.reload_doc("healthcare", "doctype", "healthcare_service_unit")
	capkpi.reload_doc("healthcare", "doctype", "healthcare_service_unit_type")
	company = capkpi.get_value("Company", {"domain": "Healthcare"}, "name")

	if company:
		capkpi.get_doc(
			{
				"doctype": "Healthcare Service Unit",
				"healthcare_service_unit_name": _("All Healthcare Service Units"),
				"is_group": 1,
				"company": company,
			}
		).insert(ignore_permissions=True)
