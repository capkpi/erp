# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import random

import capkpi
from capkpi.utils import flt
from capkpi.utils.make_random import add_random_children, get_random

import erp
from erp.accounts.doctype.payment_request.payment_request import (
	make_payment_entry,
	make_payment_request,
)
from erp.accounts.party import get_party_account_currency
from erp.setup.utils import get_exchange_rate


def work(domain="Manufacturing"):
	capkpi.set_user(capkpi.db.get_global("demo_sales_user_2"))

	for i in range(random.randint(1, 7)):
		if random.random() < 0.5:
			make_opportunity(domain)

	for i in range(random.randint(1, 3)):
		if random.random() < 0.5:
			make_quotation(domain)

	try:
		lost_reason = capkpi.get_doc(
			{"doctype": "Opportunity Lost Reason", "lost_reason": "Did not ask"}
		)
		lost_reason.save(ignore_permissions=True)
	except capkpi.exceptions.DuplicateEntryError:
		pass

	# lost quotations / inquiries
	if random.random() < 0.3:
		for i in range(random.randint(1, 3)):
			quotation = get_random("Quotation", doc=True)
			if quotation and quotation.status == "Submitted":
				quotation.declare_order_lost([{"lost_reason": "Did not ask"}])

		for i in range(random.randint(1, 3)):
			opportunity = get_random("Opportunity", doc=True)
			if opportunity and opportunity.status in ("Open", "Replied"):
				opportunity.declare_enquiry_lost([{"lost_reason": "Did not ask"}])

	for i in range(random.randint(1, 3)):
		if random.random() < 0.6:
			make_sales_order()

	if random.random() < 0.5:
		# make payment request against Sales Order
		sales_order_name = get_random("Sales Order", filters={"docstatus": 1})
		try:
			if sales_order_name:
				so = capkpi.get_doc("Sales Order", sales_order_name)
				if flt(so.per_billed) != 100:
					payment_request = make_payment_request(
						dt="Sales Order",
						dn=so.name,
						recipient_id=so.contact_email,
						submit_doc=True,
						mute_email=True,
						use_dummy_message=True,
					)

					payment_entry = capkpi.get_doc(make_payment_entry(payment_request.name))
					payment_entry.posting_date = capkpi.flags.current_date
					payment_entry.submit()
		except Exception:
			pass


def make_opportunity(domain):
	b = capkpi.get_doc(
		{
			"doctype": "Opportunity",
			"opportunity_from": "Customer",
			"party_name": capkpi.get_value("Customer", get_random("Customer"), "name"),
			"opportunity_type": "Sales",
			"with_items": 1,
			"transaction_date": capkpi.flags.current_date,
		}
	)

	add_random_children(
		b,
		"items",
		rows=4,
		randomize={
			"qty": (1, 5),
			"item_code": ("Item", {"has_variants": 0, "is_fixed_asset": 0, "domain": domain}),
		},
		unique="item_code",
	)

	b.insert()
	capkpi.db.commit()


def make_quotation(domain):
	# get open opportunites
	opportunity = get_random("Opportunity", {"status": "Open", "with_items": 1})

	if opportunity:
		from erp.crm.doctype.opportunity.opportunity import make_quotation

		qtn = capkpi.get_doc(make_quotation(opportunity))
		qtn.insert()
		capkpi.db.commit()
		qtn.submit()
		capkpi.db.commit()
	else:
		# make new directly

		# get customer, currency and exchange_rate
		customer = get_random("Customer")

		company_currency = capkpi.get_cached_value(
			"Company", erp.get_default_company(), "default_currency"
		)
		party_account_currency = get_party_account_currency(
			"Customer", customer, erp.get_default_company()
		)
		if company_currency == party_account_currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(party_account_currency, company_currency, args="for_selling")

		qtn = capkpi.get_doc(
			{
				"creation": capkpi.flags.current_date,
				"doctype": "Quotation",
				"quotation_to": "Customer",
				"party_name": customer,
				"currency": party_account_currency or company_currency,
				"conversion_rate": exchange_rate,
				"order_type": "Sales",
				"transaction_date": capkpi.flags.current_date,
			}
		)

		add_random_children(
			qtn,
			"items",
			rows=3,
			randomize={
				"qty": (1, 5),
				"item_code": ("Item", {"has_variants": "0", "is_fixed_asset": 0, "domain": domain}),
			},
			unique="item_code",
		)

		qtn.insert()
		capkpi.db.commit()
		qtn.submit()
		capkpi.db.commit()


def make_sales_order():
	q = get_random("Quotation", {"status": "Submitted"})
	if q:
		from erp.selling.doctype.quotation.quotation import make_sales_order as mso

		so = capkpi.get_doc(mso(q))
		so.transaction_date = capkpi.flags.current_date
		so.delivery_date = capkpi.utils.add_days(capkpi.flags.current_date, 10)
		so.insert()
		capkpi.db.commit()
		so.submit()
		capkpi.db.commit()
