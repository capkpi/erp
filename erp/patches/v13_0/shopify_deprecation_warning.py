import click
import capkpi


def execute():

	capkpi.reload_doc("erp_integrations", "doctype", "shopify_settings")
	if not capkpi.db.get_single_value("Shopify Settings", "enable_shopify"):
		return

	click.secho(
		"Shopify Integration is moved to a separate app and will be removed from ERP in version-14.\n"
		"Please install the app to continue using the integration: https://github.com/capkpi/ecommerce_integrations",
		fg="yellow",
	)
