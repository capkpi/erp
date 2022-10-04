# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import _
from capkpi.utils import add_days, flt, get_datetime_str, nowdate

from erp import get_default_company


def get_root_of(doctype):
	"""Get root element of a DocType with a tree structure"""
	result = capkpi.db.sql_list(
		"""select name from `tab%s`
		where lft=1 and rgt=(select max(rgt) from `tab%s` where docstatus < 2)"""
		% (doctype, doctype)
	)
	return result[0] if result else None


def get_ancestors_of(doctype, name):
	"""Get ancestor elements of a DocType with a tree structure"""
	lft, rgt = capkpi.db.get_value(doctype, name, ["lft", "rgt"])
	result = capkpi.db.sql_list(
		"""select name from `tab%s`
		where lft<%s and rgt>%s order by lft desc"""
		% (doctype, "%s", "%s"),
		(lft, rgt),
	)
	return result or []


def before_tests():
	capkpi.clear_cache()
	# complete setup if missing
	from capkpi.desk.page.setup_wizard.setup_wizard import setup_complete

	if not capkpi.get_list("Company"):
		setup_complete(
			{
				"currency": "USD",
				"full_name": "Test User",
				"company_name": "Wind Power LLC",
				"timezone": "America/New_York",
				"company_abbr": "WP",
				"industry": "Manufacturing",
				"country": "United States",
				"fy_start_date": "2011-01-01",
				"fy_end_date": "2011-12-31",
				"language": "english",
				"company_tagline": "Testing",
				"email": "test@capkpi.com",
				"password": "test",
				"chart_of_accounts": "Standard",
				"domains": ["Manufacturing"],
			}
		)

	capkpi.db.sql("delete from `tabLeave Allocation`")
	capkpi.db.sql("delete from `tabLeave Application`")
	capkpi.db.sql("delete from `tabSalary Slip`")
	capkpi.db.sql("delete from `tabItem Price`")

	capkpi.db.set_value("Stock Settings", None, "auto_insert_price_list_rate_if_missing", 0)
	enable_all_roles_and_domains()
	set_defaults_for_tests()

	capkpi.db.commit()


@capkpi.whitelist()
def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	if not (from_currency and to_currency):
		# manqala 19/09/2016: Should this be an empty return or should it throw and exception?
		return
	if from_currency == to_currency:
		return 1

	if not transaction_date:
		transaction_date = nowdate()
	currency_settings = capkpi.get_doc("Accounts Settings").as_dict()
	allow_stale_rates = currency_settings.get("allow_stale")

	filters = [
		["date", "<=", get_datetime_str(transaction_date)],
		["from_currency", "=", from_currency],
		["to_currency", "=", to_currency],
	]

	if args == "for_buying":
		filters.append(["for_buying", "=", "1"])
	elif args == "for_selling":
		filters.append(["for_selling", "=", "1"])

	if not allow_stale_rates:
		stale_days = currency_settings.get("stale_days")
		checkpoint_date = add_days(transaction_date, -stale_days)
		filters.append(["date", ">", get_datetime_str(checkpoint_date)])

	# cksgb 19/09/2016: get last entry in Currency Exchange with from_currency and to_currency.
	entries = capkpi.get_all(
		"Currency Exchange", fields=["exchange_rate"], filters=filters, order_by="date desc", limit=1
	)
	if entries:
		return flt(entries[0].exchange_rate)

	try:
		cache = capkpi.cache()
		key = "currency_exchange_rate_{0}:{1}:{2}".format(transaction_date, from_currency, to_currency)
		value = cache.get(key)

		if not value:
			import requests

			api_url = "https://api.exchangerate.host/convert"
			response = requests.get(
				api_url, params={"date": transaction_date, "from": from_currency, "to": to_currency}
			)
			# expire in 6 hours
			response.raise_for_status()
			value = response.json()["result"]
			cache.setex(name=key, time=21600, value=flt(value))
		return flt(value)
	except Exception:
		capkpi.log_error(title="Get Exchange Rate")
		capkpi.msgprint(
			_(
				"Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually"
			).format(from_currency, to_currency, transaction_date)
		)
		return 0.0


def enable_all_roles_and_domains():
	"""enable all roles and domain for testing"""
	# add all roles to users
	domains = capkpi.get_all("Domain")
	if not domains:
		return

	from capkpi.desk.page.setup_wizard.setup_wizard import add_all_roles_to

	capkpi.get_single("Domain Settings").set_active_domains([d.name for d in domains])
	add_all_roles_to("Administrator")


def set_defaults_for_tests():
	from capkpi.utils.nestedset import get_root_of

	selling_settings = capkpi.get_single("Selling Settings")
	selling_settings.customer_group = get_root_of("Customer Group")
	selling_settings.territory = get_root_of("Territory")
	selling_settings.save()


def insert_record(records):
	for r in records:
		doc = capkpi.new_doc(r.get("doctype"))
		doc.update(r)
		try:
			doc.insert(ignore_permissions=True)
		except capkpi.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0] == doc.doctype and e.args[1] == doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise


def welcome_email():
	site_name = get_default_company() or "ERP"
	title = _("Welcome to {0}").format(site_name)
	return title
