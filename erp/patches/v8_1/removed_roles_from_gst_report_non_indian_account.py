# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("core", "doctype", "has_role")
	company = capkpi.get_all("Company", filters={"country": "India"})

	if not company:
		capkpi.db.sql(
			"""
			delete from
				`tabHas Role`
			where
				parenttype = 'Report' and parent in('GST Sales Register',
					'GST Purchase Register', 'GST Itemised Sales Register',
					'GST Itemised Purchase Register', 'Eway Bill')"""
		)
