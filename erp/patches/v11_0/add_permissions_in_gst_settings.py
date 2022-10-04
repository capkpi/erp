import capkpi

from erp.regional.india.setup import add_permissions


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	capkpi.reload_doc("regional", "doctype", "lower_deduction_certificate")
	capkpi.reload_doc("regional", "doctype", "gstr_3b_report")
	add_permissions()
