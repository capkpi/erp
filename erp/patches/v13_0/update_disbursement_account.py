import capkpi


def execute():

	capkpi.reload_doc("loan_management", "doctype", "loan_type")
	capkpi.reload_doc("loan_management", "doctype", "loan")

	loan_type = capkpi.qb.DocType("Loan Type")
	loan = capkpi.qb.DocType("Loan")

	capkpi.qb.update(loan_type).set(loan_type.disbursement_account, loan_type.payment_account).run()

	capkpi.qb.update(loan).set(loan.disbursement_account, loan.payment_account).run()
