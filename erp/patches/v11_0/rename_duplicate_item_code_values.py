import capkpi


def execute():
	items = []
	items = capkpi.db.sql(
		"""select item_code from `tabItem` group by item_code having count(*) > 1""", as_dict=True
	)
	if items:
		for item in items:
			capkpi.db.sql("""update `tabItem` set item_code=name where item_code = %s""", (item.item_code))
