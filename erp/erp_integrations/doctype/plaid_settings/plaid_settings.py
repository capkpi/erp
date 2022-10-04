# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import capkpi
from capkpi import _
from capkpi.desk.doctype.tag.tag import add_tag
from capkpi.model.document import Document
from capkpi.utils import add_months, formatdate, getdate, today
from plaid.errors import ItemError

from erp.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account
from erp.erp_integrations.doctype.plaid_settings.plaid_connector import PlaidConnector


class PlaidSettings(Document):
	@staticmethod
	@capkpi.whitelist()
	def get_link_token():
		plaid = PlaidConnector()
		return plaid.get_link_token()


@capkpi.whitelist()
def get_plaid_configuration():
	if capkpi.db.get_single_value("Plaid Settings", "enabled"):
		plaid_settings = capkpi.get_single("Plaid Settings")
		return {
			"plaid_env": plaid_settings.plaid_env,
			"link_token": plaid_settings.get_link_token(),
			"client_name": capkpi.local.site,
		}

	return "disabled"


@capkpi.whitelist()
def add_institution(token, response):
	response = json.loads(response)

	plaid = PlaidConnector()
	access_token = plaid.get_access_token(token)
	bank = None

	if not capkpi.db.exists("Bank", response["institution"]["name"]):
		try:
			bank = capkpi.get_doc(
				{
					"doctype": "Bank",
					"bank_name": response["institution"]["name"],
					"plaid_access_token": access_token,
				}
			)
			bank.insert()
		except Exception:
			capkpi.log_error(capkpi.get_traceback(), title=_("Plaid Link Error"))
	else:
		bank = capkpi.get_doc("Bank", response["institution"]["name"])
		bank.plaid_access_token = access_token
		bank.save()

	return bank


@capkpi.whitelist()
def add_bank_accounts(response, bank, company):
	try:
		response = json.loads(response)
	except TypeError:
		pass

	bank = json.loads(bank)
	result = []

	default_gl_account = get_default_bank_cash_account(company, "Bank")
	if not default_gl_account:
		capkpi.throw(_("Please setup a default bank account for company {0}").format(company))

	for account in response["accounts"]:
		acc_type = capkpi.db.get_value("Bank Account Type", account["type"])
		if not acc_type:
			add_account_type(account["type"])

		acc_subtype = capkpi.db.get_value("Bank Account Subtype", account["subtype"])
		if not acc_subtype:
			add_account_subtype(account["subtype"])

		bank_account_name = "{} - {}".format(account["name"], bank["bank_name"])
		existing_bank_account = capkpi.db.exists("Bank Account", bank_account_name)

		if not existing_bank_account:
			try:
				new_account = capkpi.get_doc(
					{
						"doctype": "Bank Account",
						"bank": bank["bank_name"],
						"account": default_gl_account.account,
						"account_name": account["name"],
						"account_type": account.get("type", ""),
						"account_subtype": account.get("subtype", ""),
						"mask": account.get("mask", ""),
						"integration_id": account["id"],
						"is_company_account": 1,
						"company": company,
					}
				)
				new_account.insert()

				result.append(new_account.name)
			except capkpi.UniqueValidationError:
				capkpi.msgprint(
					_("Bank account {0} already exists and could not be created again").format(account["name"])
				)
			except Exception:
				capkpi.log_error(capkpi.get_traceback(), title=_("Plaid Link Error"))
				capkpi.throw(
					_("There was an error creating Bank Account while linking with Plaid."),
					title=_("Plaid Link Failed"),
				)

		else:
			try:
				existing_account = capkpi.get_doc("Bank Account", existing_bank_account)
				existing_account.update(
					{
						"bank": bank["bank_name"],
						"account_name": account["name"],
						"account_type": account.get("type", ""),
						"account_subtype": account.get("subtype", ""),
						"mask": account.get("mask", ""),
						"integration_id": account["id"],
					}
				)
				existing_account.save()
				result.append(existing_bank_account)
			except Exception:
				capkpi.log_error(capkpi.get_traceback(), title=_("Plaid Link Error"))
				capkpi.throw(
					_("There was an error updating Bank Account {} while linking with Plaid.").format(
						existing_bank_account
					),
					title=_("Plaid Link Failed"),
				)

	return result


def add_account_type(account_type):
	try:
		capkpi.get_doc({"doctype": "Bank Account Type", "account_type": account_type}).insert()
	except Exception:
		capkpi.throw(capkpi.get_traceback())


def add_account_subtype(account_subtype):
	try:
		capkpi.get_doc({"doctype": "Bank Account Subtype", "account_subtype": account_subtype}).insert()
	except Exception:
		capkpi.throw(capkpi.get_traceback())


@capkpi.whitelist()
def sync_transactions(bank, bank_account):
	"""Sync transactions based on the last integration date as the start date, after sync is completed
	add the transaction date of the oldest transaction as the last integration date."""
	last_transaction_date = capkpi.db.get_value("Bank Account", bank_account, "last_integration_date")
	if last_transaction_date:
		start_date = formatdate(last_transaction_date, "YYYY-MM-dd")
	else:
		start_date = formatdate(add_months(today(), -12), "YYYY-MM-dd")
	end_date = formatdate(today(), "YYYY-MM-dd")

	try:
		transactions = get_transactions(
			bank=bank, bank_account=bank_account, start_date=start_date, end_date=end_date
		)

		result = []
		for transaction in reversed(transactions):
			result += new_bank_transaction(transaction)

		if result:
			last_transaction_date = capkpi.db.get_value("Bank Transaction", result.pop(), "date")

			capkpi.logger().info(
				"Plaid added {} new Bank Transactions from '{}' between {} and {}".format(
					len(result), bank_account, start_date, end_date
				)
			)

			capkpi.db.set_value(
				"Bank Account", bank_account, "last_integration_date", last_transaction_date
			)
	except Exception:
		capkpi.log_error(capkpi.get_traceback(), _("Plaid transactions sync error"))


def get_transactions(bank, bank_account=None, start_date=None, end_date=None):
	access_token = None

	if bank_account:
		related_bank = capkpi.db.get_values(
			"Bank Account", bank_account, ["bank", "integration_id"], as_dict=True
		)
		access_token = capkpi.db.get_value("Bank", related_bank[0].bank, "plaid_access_token")
		account_id = related_bank[0].integration_id
	else:
		access_token = capkpi.db.get_value("Bank", bank, "plaid_access_token")
		account_id = None

	plaid = PlaidConnector(access_token)

	transactions = []
	try:
		transactions = plaid.get_transactions(
			start_date=start_date, end_date=end_date, account_id=account_id
		)
	except ItemError as e:
		if e.code == "ITEM_LOGIN_REQUIRED":
			msg = _("There was an error syncing transactions.") + " "
			msg += _("Please refresh or reset the Plaid linking of the Bank {}.").format(bank) + " "
			capkpi.log_error(msg, title=_("Plaid Link Refresh Required"))

	return transactions


def new_bank_transaction(transaction):
	result = []

	bank_account = capkpi.db.get_value("Bank Account", dict(integration_id=transaction["account_id"]))

	if float(transaction["amount"]) >= 0:
		debit = 0
		credit = float(transaction["amount"])
	else:
		debit = abs(float(transaction["amount"]))
		credit = 0

	status = "Pending" if transaction["pending"] == "True" else "Settled"

	tags = []
	try:
		tags += transaction["category"]
		tags += ["Plaid Cat. {}".format(transaction["category_id"])]
	except KeyError:
		pass

	if not capkpi.db.exists("Bank Transaction", dict(transaction_id=transaction["transaction_id"])):
		try:
			new_transaction = capkpi.get_doc(
				{
					"doctype": "Bank Transaction",
					"date": getdate(transaction["date"]),
					"status": status,
					"bank_account": bank_account,
					"deposit": debit,
					"withdrawal": credit,
					"currency": transaction["iso_currency_code"],
					"transaction_id": transaction["transaction_id"],
					"reference_number": transaction["payment_meta"]["reference_number"],
					"description": transaction["name"],
				}
			)
			new_transaction.insert()
			new_transaction.submit()

			for tag in tags:
				add_tag(tag, "Bank Transaction", new_transaction.name)

			result.append(new_transaction.name)

		except Exception:
			capkpi.throw(title=_("Bank transaction creation error"))

	return result


def automatic_synchronization():
	settings = capkpi.get_doc("Plaid Settings", "Plaid Settings")
	if settings.enabled == 1 and settings.automatic_sync == 1:
		enqueue_synchronization()


@capkpi.whitelist()
def enqueue_synchronization():
	plaid_accounts = capkpi.get_all(
		"Bank Account", filters={"integration_id": ["!=", ""]}, fields=["name", "bank"]
	)

	for plaid_account in plaid_accounts:
		capkpi.enqueue(
			"erp.erp_integrations.doctype.plaid_settings.plaid_settings.sync_transactions",
			bank=plaid_account.bank,
			bank_account=plaid_account.name,
		)


@capkpi.whitelist()
def get_link_token_for_update(access_token):
	plaid = PlaidConnector(access_token)
	return plaid.get_link_token(update_mode=True)
