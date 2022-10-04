import capkpi


def execute():
	capkpi.reload_doc("Payroll", "doctype", "salary_detail")
	capkpi.reload_doc("Payroll", "doctype", "salary_component")

	capkpi.db.sql("update `tabSalary Component` set is_tax_applicable=1 where type='Earning'")

	capkpi.db.sql(
		"""update `tabSalary Component` set variable_based_on_taxable_salary=1
	    where type='Deduction' and name in ('TDS', 'Tax Deducted at Source')"""
	)

	capkpi.db.sql(
		"""update `tabSalary Detail` set is_tax_applicable=1
	    where parentfield='earnings' and statistical_component=0"""
	)
	capkpi.db.sql(
		"""update `tabSalary Detail` set variable_based_on_taxable_salary=1
	    where parentfield='deductions' and salary_component in ('TDS', 'Tax Deducted at Source')"""
	)
