import capkpi
from capkpi.utils import cint


def execute():
	"""Get 'Disable CWIP Accounting value' from Asset Settings, set it in 'Enable Capital Work in Progress Accounting' field
	in Company, delete Asset Settings"""

	if capkpi.db.exists("DocType", "Asset Settings"):
		capkpi.reload_doctype("Asset Category")
		cwip_value = capkpi.db.get_single_value("Asset Settings", "disable_cwip_accounting")

		capkpi.db.sql("""UPDATE `tabAsset Category` SET enable_cwip_accounting = %s""", cint(cwip_value))

		capkpi.db.sql("""DELETE FROM `tabSingles` where doctype = 'Asset Settings'""")
		capkpi.delete_doc_if_exists("DocType", "Asset Settings")
