import capkpi


def execute():
	capkpi.reload_doc("setup", "doctype", "currency_exchange")
	capkpi.db.sql("""update `tabCurrency Exchange` set for_buying = 1, for_selling = 1""")
