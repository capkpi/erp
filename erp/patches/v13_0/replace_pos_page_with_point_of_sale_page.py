import capkpi


def execute():
	if capkpi.db.exists("Page", "point-of-sale"):
		capkpi.rename_doc("Page", "pos", "point-of-sale", 1, 1)
