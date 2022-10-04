# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("erp_integrations", "doctype", "plaid_settings")
	plaid_settings = capkpi.get_single("Plaid Settings")
	if plaid_settings.enabled:
		if not (capkpi.conf.plaid_client_id and capkpi.conf.plaid_env and capkpi.conf.plaid_secret):
			plaid_settings.enabled = 0
		else:
			plaid_settings.update(
				{
					"plaid_client_id": capkpi.conf.plaid_client_id,
					"plaid_env": capkpi.conf.plaid_env,
					"plaid_secret": capkpi.conf.plaid_secret,
				}
			)
		plaid_settings.flags.ignore_mandatory = True
		plaid_settings.save()
