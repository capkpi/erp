import capkpi

from erp.regional.india.setup import add_custom_roles_for_reports


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	add_custom_roles_for_reports()
