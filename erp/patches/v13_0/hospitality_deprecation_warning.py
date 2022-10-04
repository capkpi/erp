import click


def execute():

	click.secho(
		"Hospitality Domain is moved to a separate app and will be removed from ERP in version-14.\n"
		"When upgrading to ERP version-14, please install the app to continue using the Agriculture domain: https://github.com/capkpi/hospitality",
		fg="yellow",
	)
