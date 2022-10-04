import capkpi


def execute():
	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	capkpi.reload_doc("regional", "doctype", "lower_deduction_certificate")

	ldc = capkpi.qb.DocType("Lower Deduction Certificate").as_("ldc")
	supplier = capkpi.qb.DocType("Supplier")

	capkpi.qb.update(ldc).inner_join(supplier).on(ldc.supplier == supplier.name).set(
		ldc.tax_withholding_category, supplier.tax_withholding_category
	).where(ldc.tax_withholding_category.isnull()).run()
