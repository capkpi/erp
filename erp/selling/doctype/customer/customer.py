# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import capkpi
import capkpi.defaults
from capkpi import _, msgprint
from capkpi.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from capkpi.desk.reportview import build_match_conditions, get_filters_cond
from capkpi.model.mapper import get_mapped_doc
from capkpi.model.naming import set_name_by_naming_series, set_name_from_naming_options
from capkpi.model.rename_doc import update_linked_doctypes
from capkpi.utils import cint, cstr, flt, get_formatted_email, today
from capkpi.utils.user import get_users_with_role

from erp.accounts.party import (  # noqa
	get_dashboard_info,
	get_timeline_data,
	validate_party_accounts,
)
from erp.utilities.transaction_base import TransactionBase


class Customer(TransactionBase):
	def get_feed(self):
		return self.customer_name

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
		self.load_dashboard_info()

	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name, self.loyalty_program)
		self.set_onload("dashboard_info", info)

	def autoname(self):
		cust_master_name = capkpi.defaults.get_global_default("cust_master_name")
		if cust_master_name == "Customer Name":
			self.name = self.get_customer_name()
		elif cust_master_name == "Naming Series":
			set_name_by_naming_series(self)
		else:
			self.name = set_name_from_naming_options(capkpi.get_meta(self.doctype).autoname, self)

	def get_customer_name(self):

		if capkpi.db.get_value("Customer", self.customer_name) and not capkpi.flags.in_import:
			count = capkpi.db.sql(
				"""select ifnull(MAX(CAST(SUBSTRING_INDEX(name, ' ', -1) AS UNSIGNED)), 0) from tabCustomer
				 where name like %s""",
				"%{0} - %".format(self.customer_name),
				as_list=1,
			)[0][0]
			count = cint(count) + 1

			new_customer_name = "{0} - {1}".format(self.customer_name, cstr(count))

			msgprint(
				_("Changed customer name to '{}' as '{}' already exists.").format(
					new_customer_name, self.customer_name
				),
				title=_("Note"),
				indicator="yellow",
			)

			return new_customer_name

		return self.customer_name

	def after_insert(self):
		"""If customer created from Lead, update customer id in quotations, opportunities"""
		self.update_lead_status()

	def validate(self):
		self.flags.is_new_doc = self.is_new()
		self.flags.old_lead = self.lead_name
		validate_party_accounts(self)
		self.validate_credit_limit_on_change()
		self.set_loyalty_program()
		self.check_customer_group_change()
		self.validate_default_bank_account()
		self.validate_internal_customer()

		# set loyalty program tier
		if capkpi.db.exists("Customer", self.name):
			customer = capkpi.get_doc("Customer", self.name)
			if self.loyalty_program == customer.loyalty_program and not self.loyalty_program_tier:
				self.loyalty_program_tier = customer.loyalty_program_tier

		if self.sales_team:
			if sum(member.allocated_percentage or 0 for member in self.sales_team) != 100:
				capkpi.throw(_("Total contribution percentage should be equal to 100"))

	@capkpi.whitelist()
	def get_customer_group_details(self):
		doc = capkpi.get_doc("Customer Group", self.customer_group)
		self.accounts = []
		self.credit_limits = []
		self.payment_terms = self.default_price_list = ""

		tables = [["accounts", "account"], ["credit_limits", "credit_limit"]]
		fields = ["payment_terms", "default_price_list"]

		for row in tables:
			table, field = row[0], row[1]
			if not doc.get(table):
				continue

			for entry in doc.get(table):
				child = self.append(table)
				child.update({"company": entry.company, field: entry.get(field)})

		for field in fields:
			if not doc.get(field):
				continue
			self.update({field: doc.get(field)})

		self.save()

	def check_customer_group_change(self):
		capkpi.flags.customer_group_changed = False

		if not self.get("__islocal"):
			if self.customer_group != capkpi.db.get_value("Customer", self.name, "customer_group"):
				capkpi.flags.customer_group_changed = True

	def validate_default_bank_account(self):
		if self.default_bank_account:
			is_company_account = capkpi.db.get_value(
				"Bank Account", self.default_bank_account, "is_company_account"
			)
			if not is_company_account:
				capkpi.throw(
					_("{0} is not a company bank account").format(capkpi.bold(self.default_bank_account))
				)

	def validate_internal_customer(self):
		if not self.is_internal_customer:
			self.represents_company = ""

		internal_customer = capkpi.db.get_value(
			"Customer",
			{
				"is_internal_customer": 1,
				"represents_company": self.represents_company,
				"name": ("!=", self.name),
			},
			"name",
		)

		if internal_customer:
			capkpi.throw(
				_("Internal Customer for company {0} already exists").format(
					capkpi.bold(self.represents_company)
				)
			)

	def on_update(self):
		self.validate_name_with_customer_group()
		self.create_primary_contact()
		self.create_primary_address()

		if self.flags.old_lead != self.lead_name:
			self.update_lead_status()

		if self.flags.is_new_doc:
			self.link_lead_address_and_contact()

		self.update_customer_groups()

	def update_customer_groups(self):
		ignore_doctypes = ["Lead", "Opportunity", "POS Profile", "Tax Rule", "Pricing Rule"]
		if capkpi.flags.customer_group_changed:
			update_linked_doctypes(
				"Customer", self.name, "Customer Group", self.customer_group, ignore_doctypes
			)

	def create_primary_contact(self):
		if not self.customer_primary_contact and not self.lead_name:
			if self.mobile_no or self.email_id:
				contact = make_contact(self)
				self.db_set("customer_primary_contact", contact.name)
				self.db_set("mobile_no", self.mobile_no)
				self.db_set("email_id", self.email_id)

	def create_primary_address(self):
		from capkpi.contacts.doctype.address.address import get_address_display

		if self.flags.is_new_doc and self.get("address_line1"):
			address = make_address(self)
			address_display = get_address_display(address.name)

			self.db_set("customer_primary_address", address.name)
			self.db_set("primary_address", address_display)

	def update_lead_status(self):
		"""If Customer created from Lead, update lead status to "Converted"
		update Customer link in Quotation, Opportunity"""
		if self.lead_name:
			capkpi.db.set_value("Lead", self.lead_name, "status", "Converted")

	def link_lead_address_and_contact(self):
		if self.lead_name:
			# assign lead address and contact to customer (if already not set)
			linked_contacts_and_addresses = capkpi.get_all(
				"Dynamic Link",
				filters=[
					["parenttype", "in", ["Contact", "Address"]],
					["link_doctype", "=", "Lead"],
					["link_name", "=", self.lead_name],
				],
				fields=["parent as name", "parenttype as doctype"],
			)

			for row in linked_contacts_and_addresses:
				linked_doc = capkpi.get_doc(row.doctype, row.name)
				if not linked_doc.has_link("Customer", self.name):
					linked_doc.append("links", dict(link_doctype="Customer", link_name=self.name))
					linked_doc.save(ignore_permissions=self.flags.ignore_permissions)

	def validate_name_with_customer_group(self):
		if capkpi.db.exists("Customer Group", self.name):
			capkpi.throw(
				_(
					"A Customer Group exists with same name please change the Customer name or rename the Customer Group"
				),
				capkpi.NameError,
			)

	def validate_credit_limit_on_change(self):
		if self.get("__islocal") or not self.credit_limits:
			return

		past_credit_limits = [
			d.credit_limit
			for d in capkpi.db.get_all(
				"Customer Credit Limit",
				filters={"parent": self.name},
				fields=["credit_limit"],
				order_by="company",
			)
		]

		current_credit_limits = [
			d.credit_limit for d in sorted(self.credit_limits, key=lambda k: k.company)
		]

		if past_credit_limits == current_credit_limits:
			return

		company_record = []
		for limit in self.credit_limits:
			if limit.company in company_record:
				capkpi.throw(
					_("Credit limit is already defined for the Company {0}").format(limit.company, self.name)
				)
			else:
				company_record.append(limit.company)

			outstanding_amt = get_customer_outstanding(
				self.name, limit.company, ignore_outstanding_sales_order=limit.bypass_credit_limit_check
			)
			if flt(limit.credit_limit) < outstanding_amt:
				capkpi.throw(
					_(
						"""New credit limit is less than current outstanding amount for the customer. Credit limit has to be atleast {0}"""
					).format(outstanding_amt)
				)

	def on_trash(self):
		if self.customer_primary_contact:
			capkpi.db.sql(
				"""
				UPDATE `tabCustomer`
				SET
					customer_primary_contact=null,
					customer_primary_address=null,
					mobile_no=null,
					email_id=null,
					primary_address=null
				WHERE name=%(name)s""",
				{"name": self.name},
			)

		delete_contact_and_address("Customer", self.name)
		if self.lead_name:
			capkpi.db.sql("update `tabLead` set status='Interested' where name=%s", self.lead_name)

	def after_rename(self, olddn, newdn, merge=False):
		if capkpi.defaults.get_global_default("cust_master_name") == "Customer Name":
			capkpi.db.set(self, "customer_name", newdn)

	def set_loyalty_program(self):
		if self.loyalty_program:
			return

		loyalty_program = get_loyalty_programs(self)
		if not loyalty_program:
			return

		if len(loyalty_program) == 1:
			self.loyalty_program = loyalty_program[0]
		else:
			capkpi.msgprint(
				_("Multiple Loyalty Programs found for Customer {}. Please select manually.").format(
					capkpi.bold(self.customer_name)
				)
			)


def create_contact(contact, party_type, party, email):
	"""Create contact based on given contact name"""
	contact = contact.split(" ")

	contact = capkpi.get_doc(
		{
			"doctype": "Contact",
			"first_name": contact[0],
			"last_name": len(contact) > 1 and contact[1] or "",
		}
	)
	contact.append("email_ids", dict(email_id=email, is_primary=1))
	contact.append("links", dict(link_doctype=party_type, link_name=party))
	contact.insert()


@capkpi.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)

	target_doc = get_mapped_doc(
		"Customer",
		source_name,
		{"Customer": {"doctype": "Quotation", "field_map": {"name": "party_name"}}},
		target_doc,
		set_missing_values,
	)

	target_doc.quotation_to = "Customer"
	target_doc.run_method("set_missing_values")
	target_doc.run_method("set_other_charges")
	target_doc.run_method("calculate_taxes_and_totals")

	price_list, currency = capkpi.db.get_value(
		"Customer", {"name": source_name}, ["default_price_list", "default_currency"]
	)
	if price_list:
		target_doc.selling_price_list = price_list
	if currency:
		target_doc.currency = currency

	return target_doc


@capkpi.whitelist()
def make_opportunity(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)

	target_doc = get_mapped_doc(
		"Customer",
		source_name,
		{
			"Customer": {
				"doctype": "Opportunity",
				"field_map": {
					"name": "party_name",
					"doctype": "opportunity_from",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return target_doc


def _set_missing_values(source, target):
	address = capkpi.get_all(
		"Dynamic Link",
		{
			"link_doctype": source.doctype,
			"link_name": source.name,
			"parenttype": "Address",
		},
		["parent"],
		limit=1,
	)

	contact = capkpi.get_all(
		"Dynamic Link",
		{
			"link_doctype": source.doctype,
			"link_name": source.name,
			"parenttype": "Contact",
		},
		["parent"],
		limit=1,
	)

	if address:
		target.customer_address = address[0].parent

	if contact:
		target.contact_person = contact[0].parent


@capkpi.whitelist()
def get_loyalty_programs(doc):
	"""returns applicable loyalty programs for a customer"""

	lp_details = []
	loyalty_programs = capkpi.get_all(
		"Loyalty Program",
		fields=["name", "customer_group", "customer_territory"],
		filters={
			"auto_opt_in": 1,
			"from_date": ["<=", today()],
			"ifnull(to_date, '2500-01-01')": [">=", today()],
		},
	)

	for loyalty_program in loyalty_programs:
		if (
			not loyalty_program.customer_group
			or doc.customer_group
			in get_nested_links(
				"Customer Group", loyalty_program.customer_group, doc.flags.ignore_permissions
			)
		) and (
			not loyalty_program.customer_territory
			or doc.territory
			in get_nested_links(
				"Territory", loyalty_program.customer_territory, doc.flags.ignore_permissions
			)
		):
			lp_details.append(loyalty_program.name)

	return lp_details


def get_nested_links(link_doctype, link_name, ignore_permissions=False):
	from capkpi.desk.treeview import _get_children

	links = [link_name]
	for d in _get_children(link_doctype, link_name, ignore_permissions):
		links.append(d.value)

	return links


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_customer_list(doctype, txt, searchfield, start, page_len, filters=None):
	from erp.controllers.queries import get_fields

	fields = ["name", "customer_name", "customer_group", "territory"]

	if capkpi.db.get_default("cust_master_name") == "Customer Name":
		fields = ["name", "customer_group", "territory"]

	fields = get_fields("Customer", fields)

	match_conditions = build_match_conditions("Customer")
	match_conditions = "and {}".format(match_conditions) if match_conditions else ""

	if filters:
		filter_conditions = get_filters_cond(doctype, filters, [])
		match_conditions += "{}".format(filter_conditions)

	return capkpi.db.sql(
		"""
		select %s
		from `tabCustomer`
		where docstatus < 2
			and (%s like %s or customer_name like %s)
			{match_conditions}
		order by
			case when name like %s then 0 else 1 end,
			case when customer_name like %s then 0 else 1 end,
			name, customer_name limit %s, %s
		""".format(
			match_conditions=match_conditions
		)
		% (", ".join(fields), searchfield, "%s", "%s", "%s", "%s", "%s", "%s"),
		("%%%s%%" % txt, "%%%s%%" % txt, "%%%s%%" % txt, "%%%s%%" % txt, start, page_len),
	)


def check_credit_limit(customer, company, ignore_outstanding_sales_order=False, extra_amount=0):
	credit_limit = get_credit_limit(customer, company)
	if not credit_limit:
		return

	customer_outstanding = get_customer_outstanding(customer, company, ignore_outstanding_sales_order)
	if extra_amount > 0:
		customer_outstanding += flt(extra_amount)

	if credit_limit > 0 and flt(customer_outstanding) > credit_limit:
		msgprint(
			_("Credit limit has been crossed for customer {0} ({1}/{2})").format(
				customer, customer_outstanding, credit_limit
			)
		)

		# If not authorized person raise exception
		credit_controller_role = capkpi.db.get_single_value("Accounts Settings", "credit_controller")
		if not credit_controller_role or credit_controller_role not in capkpi.get_roles():
			# form a list of emails for the credit controller users
			credit_controller_users = get_users_with_role(credit_controller_role or "Sales Master Manager")

			# form a list of emails and names to show to the user
			credit_controller_users_formatted = [
				get_formatted_email(user).replace("<", "(").replace(">", ")")
				for user in credit_controller_users
			]
			if not credit_controller_users_formatted:
				capkpi.throw(
					_("Please contact your administrator to extend the credit limits for {0}.").format(customer)
				)

			message = """Please contact any of the following users to extend the credit limits for {0}:
				<br><br><ul><li>{1}</li></ul>""".format(
				customer, "<li>".join(credit_controller_users_formatted)
			)

			# if the current user does not have permissions to override credit limit,
			# prompt them to send out an email to the controller users
			capkpi.msgprint(
				message,
				title="Notify",
				raise_exception=1,
				primary_action={
					"label": "Send Email",
					"server_action": "erp.selling.doctype.customer.customer.send_emails",
					"args": {
						"customer": customer,
						"customer_outstanding": customer_outstanding,
						"credit_limit": credit_limit,
						"credit_controller_users_list": credit_controller_users,
					},
				},
			)


@capkpi.whitelist()
def send_emails(args):
	args = json.loads(args)
	subject = _("Credit limit reached for customer {0}").format(args.get("customer"))
	message = _("Credit limit has been crossed for customer {0} ({1}/{2})").format(
		args.get("customer"), args.get("customer_outstanding"), args.get("credit_limit")
	)
	capkpi.sendmail(
		recipients=args.get("credit_controller_users_list"), subject=subject, message=message
	)


def get_customer_outstanding(
	customer, company, ignore_outstanding_sales_order=False, cost_center=None
):
	# Outstanding based on GL Entries

	cond = ""
	if cost_center:
		lft, rgt = capkpi.get_cached_value("Cost Center", cost_center, ["lft", "rgt"])

		cond = """ and cost_center in (select name from `tabCost Center` where
			lft >= {0} and rgt <= {1})""".format(
			lft, rgt
		)

	outstanding_based_on_gle = capkpi.db.sql(
		"""
		select sum(debit) - sum(credit)
		from `tabGL Entry` where party_type = 'Customer'
		and party = %s and company=%s {0}""".format(
			cond
		),
		(customer, company),
	)

	outstanding_based_on_gle = flt(outstanding_based_on_gle[0][0]) if outstanding_based_on_gle else 0

	# Outstanding based on Sales Order
	outstanding_based_on_so = 0

	# if credit limit check is bypassed at sales order level,
	# we should not consider outstanding Sales Orders, when customer credit balance report is run
	if not ignore_outstanding_sales_order:
		outstanding_based_on_so = capkpi.db.sql(
			"""
			select sum(base_grand_total*(100 - per_billed)/100)
			from `tabSales Order`
			where customer=%s and docstatus = 1 and company=%s
			and per_billed < 100 and status != 'Closed'""",
			(customer, company),
		)

		outstanding_based_on_so = flt(outstanding_based_on_so[0][0]) if outstanding_based_on_so else 0

	# Outstanding based on Delivery Note, which are not created against Sales Order
	outstanding_based_on_dn = 0

	unmarked_delivery_note_items = capkpi.db.sql(
		"""select
			dn_item.name, dn_item.amount, dn.base_net_total, dn.base_grand_total
		from `tabDelivery Note` dn, `tabDelivery Note Item` dn_item
		where
			dn.name = dn_item.parent
			and dn.customer=%s and dn.company=%s
			and dn.docstatus = 1 and dn.status not in ('Closed', 'Stopped')
			and ifnull(dn_item.against_sales_order, '') = ''
			and ifnull(dn_item.against_sales_invoice, '') = ''
		""",
		(customer, company),
		as_dict=True,
	)

	if not unmarked_delivery_note_items:
		return outstanding_based_on_gle + outstanding_based_on_so

	si_amounts = capkpi.db.sql(
		"""
		SELECT
			dn_detail, sum(amount) from `tabSales Invoice Item`
		WHERE
			docstatus = 1
			and dn_detail in ({})
		GROUP BY dn_detail""".format(
			", ".join(capkpi.db.escape(dn_item.name) for dn_item in unmarked_delivery_note_items)
		)
	)

	si_amounts = {si_item[0]: si_item[1] for si_item in si_amounts}

	for dn_item in unmarked_delivery_note_items:
		dn_amount = flt(dn_item.amount)
		si_amount = flt(si_amounts.get(dn_item.name))

		if dn_amount > si_amount and dn_item.base_net_total:
			outstanding_based_on_dn += (
				(dn_amount - si_amount) / dn_item.base_net_total
			) * dn_item.base_grand_total

	return outstanding_based_on_gle + outstanding_based_on_so + outstanding_based_on_dn


def get_credit_limit(customer, company):
	credit_limit = None

	if customer:
		credit_limit = capkpi.db.get_value(
			"Customer Credit Limit",
			{"parent": customer, "parenttype": "Customer", "company": company},
			"credit_limit",
		)

		if not credit_limit:
			customer_group = capkpi.get_cached_value("Customer", customer, "customer_group")
			credit_limit = capkpi.db.get_value(
				"Customer Credit Limit",
				{"parent": customer_group, "parenttype": "Customer Group", "company": company},
				"credit_limit",
			)

	if not credit_limit:
		credit_limit = capkpi.get_cached_value("Company", company, "credit_limit")

	return flt(credit_limit)


def make_contact(args, is_primary_contact=1):
	contact = capkpi.get_doc(
		{
			"doctype": "Contact",
			"first_name": args.get("name"),
			"is_primary_contact": is_primary_contact,
			"links": [{"link_doctype": args.get("doctype"), "link_name": args.get("name")}],
		}
	)
	if args.get("email_id"):
		contact.add_email(args.get("email_id"), is_primary=True)
	if args.get("mobile_no"):
		contact.add_phone(args.get("mobile_no"), is_primary_mobile_no=True)
	contact.insert()

	return contact


def make_address(args, is_primary_address=1):
	reqd_fields = []
	for field in ["city", "country"]:
		if not args.get(field):
			reqd_fields.append("<li>" + field.title() + "</li>")

	if reqd_fields:
		msg = _("Following fields are mandatory to create address:")
		capkpi.throw(
			"{0} <br><br> <ul>{1}</ul>".format(msg, "\n".join(reqd_fields)),
			title=_("Missing Values Required"),
		)

	address = capkpi.get_doc(
		{
			"doctype": "Address",
			"address_title": args.get("name"),
			"address_line1": args.get("address_line1"),
			"address_line2": args.get("address_line2"),
			"city": args.get("city"),
			"state": args.get("state"),
			"pincode": args.get("pincode"),
			"country": args.get("country"),
			"links": [{"link_doctype": args.get("doctype"), "link_name": args.get("name")}],
		}
	).insert()

	return address


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_customer_primary_contact(doctype, txt, searchfield, start, page_len, filters):
	customer = filters.get("customer")
	return capkpi.db.sql(
		"""
		select `tabContact`.name from `tabContact`, `tabDynamic Link`
			where `tabContact`.name = `tabDynamic Link`.parent and `tabDynamic Link`.link_name = %(customer)s
			and `tabDynamic Link`.link_doctype = 'Customer'
			and `tabContact`.name like %(txt)s
		""",
		{"customer": customer, "txt": "%%%s%%" % txt},
	)
