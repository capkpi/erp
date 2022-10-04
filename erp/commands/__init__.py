# Copyright (c) 2015, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import click
import capkpi
from capkpi.commands import get_site, pass_context


def call_command(cmd, context):
	return click.Context(cmd, obj=context).forward(cmd)


@click.command("make-demo")
@click.option("--site", help="site name")
@click.option("--domain", default="Manufacturing")
@click.option("--days", default=100, help="Run the demo for so many days. Default 100")
@click.option(
	"--resume", default=False, is_flag=True, help="Continue running the demo for given days"
)
@click.option("--reinstall", default=False, is_flag=True, help="Reinstall site before demo")
@pass_context
def make_demo(context, site, domain="Manufacturing", days=100, resume=False, reinstall=False):
	"Reinstall site and setup demo"
	from capkpi.commands.site import _reinstall
	from capkpi.installer import install_app

	site = get_site(context)

	if resume:
		with capkpi.init_site(site):
			capkpi.connect()
			from erp.demo import demo

			demo.simulate(days=days)
	else:
		if reinstall:
			_reinstall(site, yes=True)
		with capkpi.init_site(site=site):
			capkpi.connect()
			if not "erp" in capkpi.get_installed_apps():
				install_app("erp")

			# import needs site
			from erp.demo import demo

			demo.make(domain, days)


commands = [make_demo]
