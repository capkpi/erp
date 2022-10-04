# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi import _
from capkpi.model.document import Document
from capkpi.query_builder.custom import ConstantColumn
from capkpi.utils import flt

from erp import get_company_currency
from erp.accounts.doctype.bank_transaction.bank_transaction import get_paid_amount
from erp.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement import (
	get_amounts_not_reflected_in_system,
	get_entries,
)
from erp.accounts.utils import get_balance_on


class BankReconciliationTool(Document):
	pass


@capkpi.whitelist()
def get_bank_transactions(bank_account, from_date=None, to_date=None):
	# returns bank transactions for a bank account
	filters = []
	filters.append(["bank_account", "=", bank_account])
	filters.append(["docstatus", "=", 1])
	filters.append(["unallocated_amount", ">", 0])
	if to_date:
		filters.append(["date", "<=", to_date])
	if from_date:
		filters.append(["date", ">=", from_date])
	transactions = capkpi.get_all(
		"Bank Transaction",
		fields=[
			"date",
			"deposit",
			"withdrawal",
			"currency",
			"description",
			"name",
			"bank_account",
			"company",
			"unallocated_amount",
			"reference_number",
			"party_type",
			"party",
		],
		filters=filters,
	)
	return transactions


@capkpi.whitelist()
def get_account_balance(bank_account, till_date):
	# returns account balance till the specified date
	account = capkpi.db.get_value("Bank Account", bank_account, "account")
	filters = capkpi._dict(
		{"account": account, "report_date": till_date, "include_pos_transactions": 1}
	)
	data = get_entries(filters)

	balance_as_per_system = get_balance_on(filters["account"], filters["report_date"])

	total_debit, total_credit = 0, 0
	for d in data:
		total_debit += flt(d.debit)
		total_credit += flt(d.credit)

	amounts_not_reflected_in_system = get_amounts_not_reflected_in_system(filters)

	bank_bal = (
		flt(balance_as_per_system)
		- flt(total_debit)
		+ flt(total_credit)
		+ amounts_not_reflected_in_system
	)

	return bank_bal


@capkpi.whitelist()
def update_bank_transaction(bank_transaction_name, reference_number, party_type=None, party=None):
	# updates bank transaction based on the new parameters provided by the user from Vouchers
	bank_transaction = capkpi.get_doc("Bank Transaction", bank_transaction_name)
	bank_transaction.reference_number = reference_number
	bank_transaction.party_type = party_type
	bank_transaction.party = party
	bank_transaction.save()
	return capkpi.db.get_all(
		"Bank Transaction",
		filters={"name": bank_transaction_name},
		fields=[
			"date",
			"deposit",
			"withdrawal",
			"currency",
			"description",
			"name",
			"bank_account",
			"company",
			"unallocated_amount",
			"reference_number",
			"party_type",
			"party",
		],
	)[0]


@capkpi.whitelist()
def create_journal_entry_bts(
	bank_transaction_name,
	reference_number=None,
	reference_date=None,
	posting_date=None,
	entry_type=None,
	second_account=None,
	mode_of_payment=None,
	party_type=None,
	party=None,
	allow_edit=None,
):
	# Create a new journal entry based on the bank transaction
	bank_transaction = capkpi.db.get_values(
		"Bank Transaction",
		bank_transaction_name,
		fieldname=["name", "deposit", "withdrawal", "bank_account"],
		as_dict=True,
	)[0]
	company_account = capkpi.get_value("Bank Account", bank_transaction.bank_account, "account")
	account_type = capkpi.db.get_value("Account", second_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		if not (party_type and party):
			capkpi.throw(
				_("Party Type and Party is required for Receivable / Payable account {0}").format(
					second_account
				)
			)
	accounts = []
	# Multi Currency?
	accounts.append(
		{
			"account": second_account,
			"credit_in_account_currency": bank_transaction.deposit if bank_transaction.deposit > 0 else 0,
			"debit_in_account_currency": bank_transaction.withdrawal
			if bank_transaction.withdrawal > 0
			else 0,
			"party_type": party_type,
			"party": party,
		}
	)

	accounts.append(
		{
			"account": company_account,
			"bank_account": bank_transaction.bank_account,
			"credit_in_account_currency": bank_transaction.withdrawal
			if bank_transaction.withdrawal > 0
			else 0,
			"debit_in_account_currency": bank_transaction.deposit if bank_transaction.deposit > 0 else 0,
		}
	)

	company = capkpi.get_value("Account", company_account, "company")

	journal_entry_dict = {
		"voucher_type": entry_type,
		"company": company,
		"posting_date": posting_date,
		"cheque_date": reference_date,
		"cheque_no": reference_number,
		"mode_of_payment": mode_of_payment,
	}
	journal_entry = capkpi.new_doc("Journal Entry")
	journal_entry.update(journal_entry_dict)
	journal_entry.set("accounts", accounts)

	if allow_edit:
		return journal_entry

	journal_entry.insert()
	journal_entry.submit()

	if bank_transaction.deposit > 0:
		paid_amount = bank_transaction.deposit
	else:
		paid_amount = bank_transaction.withdrawal

	vouchers = json.dumps(
		[{"payment_doctype": "Journal Entry", "payment_name": journal_entry.name, "amount": paid_amount}]
	)

	return reconcile_vouchers(bank_transaction.name, vouchers)


@capkpi.whitelist()
def create_payment_entry_bts(
	bank_transaction_name,
	reference_number=None,
	reference_date=None,
	party_type=None,
	party=None,
	posting_date=None,
	mode_of_payment=None,
	project=None,
	cost_center=None,
	allow_edit=None,
):
	# Create a new payment entry based on the bank transaction
	bank_transaction = capkpi.db.get_values(
		"Bank Transaction",
		bank_transaction_name,
		fieldname=["name", "unallocated_amount", "deposit", "bank_account"],
		as_dict=True,
	)[0]
	paid_amount = bank_transaction.unallocated_amount
	payment_type = "Receive" if bank_transaction.deposit > 0 else "Pay"

	company_account = capkpi.get_value("Bank Account", bank_transaction.bank_account, "account")
	company = capkpi.get_value("Account", company_account, "company")
	payment_entry_dict = {
		"company": company,
		"payment_type": payment_type,
		"reference_no": reference_number,
		"reference_date": reference_date,
		"party_type": party_type,
		"party": party,
		"posting_date": posting_date,
		"paid_amount": paid_amount,
		"received_amount": paid_amount,
	}
	payment_entry = capkpi.new_doc("Payment Entry")

	payment_entry.update(payment_entry_dict)

	if mode_of_payment:
		payment_entry.mode_of_payment = mode_of_payment
	if project:
		payment_entry.project = project
	if cost_center:
		payment_entry.cost_center = cost_center
	if payment_type == "Receive":
		payment_entry.paid_to = company_account
	else:
		payment_entry.paid_from = company_account

	payment_entry.validate()

	if allow_edit:
		return payment_entry

	payment_entry.insert()

	payment_entry.submit()
	vouchers = json.dumps(
		[{"payment_doctype": "Payment Entry", "payment_name": payment_entry.name, "amount": paid_amount}]
	)
	return reconcile_vouchers(bank_transaction.name, vouchers)


@capkpi.whitelist()
def reconcile_vouchers(bank_transaction_name, vouchers):
	# updated clear date of all the vouchers based on the bank transaction
	vouchers = json.loads(vouchers)
	transaction = capkpi.get_doc("Bank Transaction", bank_transaction_name)
	company_account = capkpi.db.get_value("Bank Account", transaction.bank_account, "account")

	if transaction.unallocated_amount == 0:
		capkpi.throw(_("This bank transaction is already fully reconciled"))
	total_amount = 0
	for voucher in vouchers:
		voucher["payment_entry"] = capkpi.get_doc(voucher["payment_doctype"], voucher["payment_name"])
		total_amount += get_paid_amount(
			capkpi._dict(
				{
					"payment_document": voucher["payment_doctype"],
					"payment_entry": voucher["payment_name"],
				}
			),
			transaction.currency,
			company_account,
		)

	if total_amount > transaction.unallocated_amount:
		capkpi.throw(
			_(
				"The sum total of amounts of all selected vouchers should be less than the unallocated amount of the bank transaction"
			)
		)
	account = capkpi.db.get_value("Bank Account", transaction.bank_account, "account")

	for voucher in vouchers:
		gl_entry = capkpi.db.get_value(
			"GL Entry",
			dict(
				account=account, voucher_type=voucher["payment_doctype"], voucher_no=voucher["payment_name"]
			),
			["credit", "debit"],
			as_dict=1,
		)
		gl_amount, transaction_amount = (
			(gl_entry.credit, transaction.deposit)
			if gl_entry.credit > 0
			else (gl_entry.debit, transaction.withdrawal)
		)
		allocated_amount = gl_amount if gl_amount >= transaction_amount else transaction_amount

		transaction.append(
			"payment_entries",
			{
				"payment_document": voucher["payment_entry"].doctype,
				"payment_entry": voucher["payment_entry"].name,
				"allocated_amount": allocated_amount,
			},
		)

	transaction.save()
	transaction.update_allocations()
	return capkpi.get_doc("Bank Transaction", bank_transaction_name)


@capkpi.whitelist()
def get_linked_payments(bank_transaction_name, document_types=None):
	# get all matching payments for a bank transaction
	transaction = capkpi.get_doc("Bank Transaction", bank_transaction_name)
	bank_account = capkpi.db.get_values(
		"Bank Account", transaction.bank_account, ["account", "company"], as_dict=True
	)[0]
	(account, company) = (bank_account.account, bank_account.company)
	matching = check_matching(account, company, transaction, document_types)
	return matching


def check_matching(bank_account, company, transaction, document_types):
	# combine all types of vouchers
	subquery = get_queries(bank_account, company, transaction, document_types)
	filters = {
		"amount": transaction.unallocated_amount,
		"payment_type": "Receive" if transaction.deposit > 0 else "Pay",
		"reference_no": transaction.reference_number,
		"party_type": transaction.party_type,
		"party": transaction.party,
		"bank_account": bank_account,
	}

	matching_vouchers = []

	matching_vouchers.extend(get_loan_vouchers(bank_account, transaction, document_types, filters))

	for query in subquery:
		matching_vouchers.extend(
			capkpi.db.sql(
				query,
				filters,
			)
		)

	return sorted(matching_vouchers, key=lambda x: x[0], reverse=True) if matching_vouchers else []


def get_queries(bank_account, company, transaction, document_types):
	# get queries to get matching vouchers
	amount_condition = "=" if "exact_match" in document_types else "<="
	account_from_to = "paid_to" if transaction.deposit > 0 else "paid_from"
	queries = []

	if "payment_entry" in document_types:
		pe_amount_matching = get_pe_matching_query(amount_condition, account_from_to, transaction)
		queries.extend([pe_amount_matching])

	if "journal_entry" in document_types:
		je_amount_matching = get_je_matching_query(amount_condition, transaction)
		queries.extend([je_amount_matching])

	if transaction.deposit > 0 and "sales_invoice" in document_types:
		si_amount_matching = get_si_matching_query(amount_condition)
		queries.extend([si_amount_matching])

	if transaction.withdrawal > 0:
		if "purchase_invoice" in document_types:
			pi_amount_matching = get_pi_matching_query(amount_condition)
			queries.extend([pi_amount_matching])

		if "expense_claim" in document_types:
			ec_amount_matching = get_ec_matching_query(bank_account, company, amount_condition)
			queries.extend([ec_amount_matching])

	return queries


def get_loan_vouchers(bank_account, transaction, document_types, filters):
	vouchers = []
	amount_condition = True if "exact_match" in document_types else False

	if transaction.withdrawal > 0 and "loan_disbursement" in document_types:
		vouchers.extend(get_ld_matching_query(bank_account, amount_condition, filters))

	if transaction.deposit > 0 and "loan_repayment" in document_types:
		vouchers.extend(get_lr_matching_query(bank_account, amount_condition, filters))

	return vouchers


def get_ld_matching_query(bank_account, amount_condition, filters):
	loan_disbursement = capkpi.qb.DocType("Loan Disbursement")
	matching_reference = loan_disbursement.reference_number == filters.get("reference_number")
	matching_party = loan_disbursement.applicant_type == filters.get(
		"party_type"
	) and loan_disbursement.applicant == filters.get("party")

	rank = capkpi.qb.terms.Case().when(matching_reference, 1).else_(0)

	rank1 = capkpi.qb.terms.Case().when(matching_party, 1).else_(0)

	query = (
		capkpi.qb.from_(loan_disbursement)
		.select(
			rank + rank1 + 1,
			ConstantColumn("Loan Disbursement").as_("doctype"),
			loan_disbursement.name,
			loan_disbursement.disbursed_amount,
			loan_disbursement.reference_number,
			loan_disbursement.reference_date,
			loan_disbursement.applicant_type,
			loan_disbursement.disbursement_date,
		)
		.where(loan_disbursement.docstatus == 1)
		.where(loan_disbursement.clearance_date.isnull())
		.where(loan_disbursement.disbursement_account == bank_account)
	)

	if amount_condition:
		query.where(loan_disbursement.disbursed_amount == filters.get("amount"))
	else:
		query.where(loan_disbursement.disbursed_amount <= filters.get("amount"))

	vouchers = query.run(as_list=True)

	return vouchers


def get_lr_matching_query(bank_account, amount_condition, filters):
	loan_repayment = capkpi.qb.DocType("Loan Repayment")
	matching_reference = loan_repayment.reference_number == filters.get("reference_number")
	matching_party = loan_repayment.applicant_type == filters.get(
		"party_type"
	) and loan_repayment.applicant == filters.get("party")

	rank = capkpi.qb.terms.Case().when(matching_reference, 1).else_(0)

	rank1 = capkpi.qb.terms.Case().when(matching_party, 1).else_(0)

	query = (
		capkpi.qb.from_(loan_repayment)
		.select(
			rank + rank1 + 1,
			ConstantColumn("Loan Repayment").as_("doctype"),
			loan_repayment.name,
			loan_repayment.amount_paid,
			loan_repayment.reference_number,
			loan_repayment.reference_date,
			loan_repayment.applicant_type,
			loan_repayment.posting_date,
		)
		.where(loan_repayment.docstatus == 1)
		.where(loan_repayment.repay_from_salary == 0)
		.where(loan_repayment.clearance_date.isnull())
		.where(loan_repayment.payment_account == bank_account)
	)

	if amount_condition:
		query.where(loan_repayment.amount_paid == filters.get("amount"))
	else:
		query.where(loan_repayment.amount_paid <= filters.get("amount"))

	vouchers = query.run()

	return vouchers


def get_pe_matching_query(amount_condition, account_from_to, transaction):
	# get matching payment entries query
	if transaction.deposit > 0:
		currency_field = "paid_to_account_currency as currency"
	else:
		currency_field = "paid_from_account_currency as currency"
	return f"""
	SELECT
		(CASE WHEN reference_no=%(reference_no)s THEN 1 ELSE 0 END
		+ CASE WHEN (party_type = %(party_type)s AND party = %(party)s ) THEN 1 ELSE 0  END
		+ 1 ) AS rank,
		'Payment Entry' as doctype,
		name,
		paid_amount,
		reference_no,
		reference_date,
		party,
		party_type,
		posting_date,
		{currency_field}
	FROM
		`tabPayment Entry`
	WHERE
		paid_amount {amount_condition} %(amount)s
		AND docstatus = 1
		AND payment_type IN (%(payment_type)s, 'Internal Transfer')
		AND ifnull(clearance_date, '') = ""
		AND {account_from_to} = %(bank_account)s
	"""


def get_je_matching_query(amount_condition, transaction):
	# get matching journal entry query

	# We have mapping at the bank level
	# So one bank could have both types of bank accounts like asset and liability
	# So cr_or_dr should be judged only on basis of withdrawal and deposit and not account type
	cr_or_dr = "credit" if transaction.withdrawal > 0 else "debit"

	return f"""

		SELECT
			(CASE WHEN je.cheque_no=%(reference_no)s THEN 1 ELSE 0 END
			+ 1) AS rank ,
			'Journal Entry' as doctype,
			je.name,
			jea.{cr_or_dr}_in_account_currency as paid_amount,
			je.cheque_no as reference_no,
			je.cheque_date as reference_date,
			je.pay_to_recd_from as party,
			jea.party_type,
			je.posting_date,
			jea.account_currency as currency
		FROM
			`tabJournal Entry Account` as jea
		JOIN
			`tabJournal Entry` as je
		ON
			jea.parent = je.name
		WHERE
			(je.clearance_date is null or je.clearance_date='0000-00-00')
			AND jea.account = %(bank_account)s
			AND jea.{cr_or_dr}_in_account_currency {amount_condition} %(amount)s
			AND je.docstatus = 1
	"""


def get_si_matching_query(amount_condition):
	# get matchin sales invoice query
	return f"""
		SELECT
			( CASE WHEN si.customer = %(party)s  THEN 1 ELSE 0  END
			+ 1 ) AS rank,
			'Sales Invoice' as doctype,
			si.name,
			sip.amount as paid_amount,
			'' as reference_no,
			'' as reference_date,
			si.customer as party,
			'Customer' as party_type,
			si.posting_date,
			si.currency

		FROM
			`tabSales Invoice Payment` as sip
		JOIN
			`tabSales Invoice` as si
		ON
			sip.parent = si.name
		WHERE (sip.clearance_date is null or sip.clearance_date='0000-00-00')
			AND sip.account = %(bank_account)s
			AND sip.amount {amount_condition} %(amount)s
			AND si.docstatus = 1
	"""


def get_pi_matching_query(amount_condition):
	# get matching purchase invoice query
	return f"""
		SELECT
			( CASE WHEN supplier = %(party)s THEN 1 ELSE 0 END
			+ 1 ) AS rank,
			'Purchase Invoice' as doctype,
			name,
			paid_amount,
			'' as reference_no,
			'' as reference_date,
			supplier as party,
			'Supplier' as party_type,
			posting_date,
			currency
		FROM
			`tabPurchase Invoice`
		WHERE
			paid_amount {amount_condition} %(amount)s
			AND docstatus = 1
			AND is_paid = 1
			AND ifnull(clearance_date, '') = ""
			AND cash_bank_account  = %(bank_account)s
	"""


def get_ec_matching_query(bank_account, company, amount_condition):
	# get matching Expense Claim query
	mode_of_payments = [
		x["parent"]
		for x in capkpi.db.get_all(
			"Mode of Payment Account", filters={"default_account": bank_account}, fields=["parent"]
		)
	]
	mode_of_payments = "('" + "', '".join(mode_of_payments) + "' )"
	company_currency = get_company_currency(company)
	return f"""
		SELECT
			( CASE WHEN employee = %(party)s THEN 1 ELSE 0 END
			+ 1 ) AS rank,
			'Expense Claim' as doctype,
			name,
			total_sanctioned_amount as paid_amount,
			'' as reference_no,
			'' as reference_date,
			employee as party,
			'Employee' as party_type,
			posting_date,
			'{company_currency}' as currency
		FROM
			`tabExpense Claim`
		WHERE
			total_sanctioned_amount {amount_condition} %(amount)s
			AND docstatus = 1
			AND is_paid = 1
			AND ifnull(clearance_date, '') = ""
			AND mode_of_payment in {mode_of_payments}
	"""
