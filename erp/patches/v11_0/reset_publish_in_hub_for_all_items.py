import capkpi


def execute():
	capkpi.reload_doc("stock", "doctype", "item")
	capkpi.db.sql("""update `tabItem` set publish_in_hub = 0""")
