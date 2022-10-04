import click


def execute():
	click.secho(
		"DATEV reports are moved to a separate app and will be removed from ERP in version-14.\n"
		"Please install the app to continue using them: https://github.com/alyf-de/erp_datev",
		fg="yellow",
	)
