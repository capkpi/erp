import capkpi

from erp.setup.setup_wizard.operations.install_fixtures import add_market_segments


def execute():
	capkpi.reload_doc("crm", "doctype", "market_segment")

	capkpi.local.lang = capkpi.db.get_default("lang") or "en"

	add_market_segments()
