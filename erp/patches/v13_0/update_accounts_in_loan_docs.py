import capkpi


def execute():

	capkpi.reload_doc("loan_management", "doctype", "loan")
	capkpi.reload_doc("loan_management", "doctype", "loan_disbursement")
	capkpi.reload_doc("loan_management", "doctype", "loan_repayment")

	ld = capkpi.qb.DocType("Loan Disbursement").as_("ld")
	lr = capkpi.qb.DocType("Loan Repayment").as_("lr")
	loan = capkpi.qb.DocType("Loan")

	capkpi.qb.update(ld).inner_join(loan).on(loan.name == ld.against_loan).set(
		ld.disbursement_account, loan.disbursement_account
	).set(ld.loan_account, loan.loan_account).where(ld.docstatus < 2).run()

	capkpi.qb.update(lr).inner_join(loan).on(loan.name == lr.against_loan).set(
		lr.payment_account, loan.payment_account
	).set(lr.loan_account, loan.loan_account).set(
		lr.penalty_income_account, loan.penalty_income_account
	).where(
		lr.docstatus < 2
	).run()
