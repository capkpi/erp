import capkpi


def execute():
	capkpi.reload_doc("loan_management", "doctype", "loan")
	loan = capkpi.qb.DocType("Loan")

	for company in capkpi.get_all("Company", pluck="name"):
		default_cost_center = capkpi.db.get_value("Company", company, "cost_center")
		capkpi.qb.update(loan).set(loan.cost_center, default_cost_center).where(
			loan.company == company
		).run()
