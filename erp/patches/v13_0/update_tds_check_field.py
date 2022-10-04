import capkpi


def execute():
	if capkpi.db.has_table("Tax Withholding Category") and capkpi.db.has_column(
		"Tax Withholding Category", "round_off_tax_amount"
	):
		capkpi.db.sql(
			"""
			UPDATE `tabTax Withholding Category` set round_off_tax_amount = 0
			WHERE round_off_tax_amount IS NULL
		"""
		)
