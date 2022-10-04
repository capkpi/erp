import capkpi


def execute():
	capkpi.reload_doc("setup", "doctype", "uom")

	uom = capkpi.qb.DocType("UOM")

	(
		capkpi.qb.update(uom)
		.set(uom.enabled, 1)
		.where(uom.creation >= "2021-10-18")  # date when this field was released
	).run()
