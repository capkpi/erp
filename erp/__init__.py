import inspect

import capkpi

from erp.hooks import regional_overrides

__version__ = "13.39.2"


def get_default_company(user=None):
	"""Get default company for user"""
	from capkpi.defaults import get_user_default_as_list

	if not user:
		user = capkpi.session.user

	companies = get_user_default_as_list(user, "company")
	if companies:
		default_company = companies[0]
	else:
		default_company = capkpi.db.get_single_value("Global Defaults", "default_company")

	return default_company


def get_default_currency():
	"""Returns the currency of the default company"""
	company = get_default_company()
	if company:
		return capkpi.get_cached_value("Company", company, "default_currency")


def get_default_cost_center(company):
	"""Returns the default cost center of the company"""
	if not company:
		return None

	if not capkpi.flags.company_cost_center:
		capkpi.flags.company_cost_center = {}
	if not company in capkpi.flags.company_cost_center:
		capkpi.flags.company_cost_center[company] = capkpi.get_cached_value(
			"Company", company, "cost_center"
		)
	return capkpi.flags.company_cost_center[company]


def get_company_currency(company):
	"""Returns the default company currency"""
	if not capkpi.flags.company_currency:
		capkpi.flags.company_currency = {}
	if not company in capkpi.flags.company_currency:
		capkpi.flags.company_currency[company] = capkpi.db.get_value(
			"Company", company, "default_currency", cache=True
		)
	return capkpi.flags.company_currency[company]


def set_perpetual_inventory(enable=1, company=None):
	if not company:
		company = "_Test Company" if capkpi.flags.in_test else get_default_company()

	company = capkpi.get_doc("Company", company)
	company.enable_perpetual_inventory = enable
	company.save()


def encode_company_abbr(name, company=None, abbr=None):
	"""Returns name encoded with company abbreviation"""
	company_abbr = abbr or capkpi.get_cached_value("Company", company, "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != company_abbr.lower():
		parts.append(company_abbr)

	return " - ".join(parts)


def is_perpetual_inventory_enabled(company):
	if not company:
		company = "_Test Company" if capkpi.flags.in_test else get_default_company()

	if not hasattr(capkpi.local, "enable_perpetual_inventory"):
		capkpi.local.enable_perpetual_inventory = {}

	if not company in capkpi.local.enable_perpetual_inventory:
		capkpi.local.enable_perpetual_inventory[company] = (
			capkpi.get_cached_value("Company", company, "enable_perpetual_inventory") or 0
		)

	return capkpi.local.enable_perpetual_inventory[company]


def get_default_finance_book(company=None):
	if not company:
		company = get_default_company()

	if not hasattr(capkpi.local, "default_finance_book"):
		capkpi.local.default_finance_book = {}

	if not company in capkpi.local.default_finance_book:
		capkpi.local.default_finance_book[company] = capkpi.get_cached_value(
			"Company", company, "default_finance_book"
		)

	return capkpi.local.default_finance_book[company]


def get_party_account_type(party_type):
	if not hasattr(capkpi.local, "party_account_types"):
		capkpi.local.party_account_types = {}

	if not party_type in capkpi.local.party_account_types:
		capkpi.local.party_account_types[party_type] = (
			capkpi.db.get_value("Party Type", party_type, "account_type") or ""
		)

	return capkpi.local.party_account_types[party_type]


def get_region(company=None):
	"""Return the default country based on flag, company or global settings

	You can also set global company flag in `capkpi.flags.company`
	"""
	if company or capkpi.flags.company:
		return capkpi.get_cached_value("Company", company or capkpi.flags.company, "country")
	elif capkpi.flags.country:
		return capkpi.flags.country
	else:
		return capkpi.get_system_settings("country")


def allow_regional(fn):
	"""Decorator to make a function regionally overridable

	Example:
	@erp.allow_regional
	def myfunction():
	  pass"""

	def caller(*args, **kwargs):
		region = get_region()
		fn_name = inspect.getmodule(fn).__name__ + "." + fn.__name__
		if region in regional_overrides and fn_name in regional_overrides[region]:
			return capkpi.get_attr(regional_overrides[region][fn_name])(*args, **kwargs)
		else:
			return fn(*args, **kwargs)

	return caller


@capkpi.whitelist()
def get_last_membership(member):
	"""Returns last membership if exists"""
	last_membership = capkpi.get_all(
		"Membership",
		"name,to_date,membership_type",
		dict(member=member, paid=1),
		order_by="to_date desc",
		limit=1,
	)

	if last_membership:
		return last_membership[0]
