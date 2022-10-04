import capkpi


def execute():
	name = capkpi.db.sql(
		""" select name from `tabPatch Log` \
		where \
			patch like 'execute:capkpi.db.sql("update `tabProduction Order` pro set description%' """
	)
	if not name:
		capkpi.db.sql(
			"update `tabProduction Order` pro \
			set \
				description = (select description from tabItem where name=pro.production_item) \
			where \
				ifnull(description, '') = ''"
		)
