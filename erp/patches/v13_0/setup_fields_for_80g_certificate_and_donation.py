import capkpi

from erp.regional.india.setup import make_custom_fields


def execute():
	if capkpi.get_all("Company", filters={"country": "India"}):
		capkpi.reload_doc("accounts", "doctype", "POS Invoice")
		capkpi.reload_doc("accounts", "doctype", "POS Invoice Item")

		make_custom_fields()

		if not capkpi.db.exists("Party Type", "Donor"):
			capkpi.get_doc(
				{"doctype": "Party Type", "party_type": "Donor", "account_type": "Receivable"}
			).insert(ignore_permissions=True)
