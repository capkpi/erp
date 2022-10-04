import capkpi
from capkpi.custom.doctype.custom_field.custom_field import create_custom_fields

from erp.domains.healthcare import data


def execute():
	if "Healthcare" not in capkpi.get_active_domains():
		return

	if data["custom_fields"]:
		create_custom_fields(data["custom_fields"])
