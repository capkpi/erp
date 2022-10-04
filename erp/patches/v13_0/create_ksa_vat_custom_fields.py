import capkpi

from erp.regional.saudi_arabia.setup import make_custom_fields


def execute():
	company = capkpi.get_all("Company", filters={"country": "Saudi Arabia"})
	if not company:
		return

	make_custom_fields()
