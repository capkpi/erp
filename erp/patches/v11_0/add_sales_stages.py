import capkpi

from erp.setup.setup_wizard.operations.install_fixtures import add_sale_stages


def execute():
	capkpi.reload_doc("crm", "doctype", "sales_stage")

	capkpi.local.lang = capkpi.db.get_default("lang") or "en"

	add_sale_stages()
