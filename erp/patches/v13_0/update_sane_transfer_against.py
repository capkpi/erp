import capkpi


def execute():
	bom = capkpi.qb.DocType("BOM")

	(
		capkpi.qb.update(bom)
		.set(bom.transfer_material_against, "Work Order")
		.where(bom.with_operations == 0)
	).run()
