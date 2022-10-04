# Copyright (c) 2020, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi


def execute():
	count = capkpi.db.sql(
		"SELECT COUNT(*) FROM `tabSingles` WHERE doctype='Amazon MWS Settings' AND field='enable_sync';"
	)[0][0]
	if count == 0:
		capkpi.db.sql(
			"UPDATE `tabSingles` SET field='enable_sync' WHERE doctype='Amazon MWS Settings' AND field='enable_synch';"
		)

	capkpi.reload_doc("ERP Integrations", "doctype", "Amazon MWS Settings")
