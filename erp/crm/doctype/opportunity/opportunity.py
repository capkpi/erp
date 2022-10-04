# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import capkpi
from capkpi import _
from capkpi.email.inbox import link_communication_to_document
from capkpi.model.mapper import get_mapped_doc
from capkpi.utils import cint, get_fullname

from erp.accounts.party import get_party_account_currency
from erp.setup.utils import get_exchange_rate
from erp.utilities.transaction_base import TransactionBase


class Opportunity(TransactionBase):
	def after_insert(self):
		if self.opportunity_from == "Lead":
			capkpi.get_doc("Lead", self.party_name).set_status(update=True)

	def validate(self):
		self._prev = capkpi._dict(
			{
				"contact_date": capkpi.db.get_value("Opportunity", self.name, "contact_date")
				if (not cint(self.get("__islocal")))
				else None,
				"contact_by": capkpi.db.get_value("Opportunity", self.name, "contact_by")
				if (not cint(self.get("__islocal")))
				else None,
			}
		)

		self.make_new_lead_if_required()

		self.validate_item_details()
		self.validate_uom_is_integer("uom", "qty")
		self.validate_cust_name()
		self.map_fields()

		if not self.title:
			self.title = self.customer_name

		if not self.with_items:
			self.items = []

	def map_fields(self):
		for field in self.meta.fields:
			if not self.get(field.fieldname):
				try:
					value = capkpi.db.get_value(self.opportunity_from, self.party_name, field.fieldname)
					capkpi.db.set(self, field.fieldname, value)
				except Exception:
					continue

	def make_new_lead_if_required(self):
		"""Set lead against new opportunity"""
		if (not self.get("party_name")) and self.contact_email:
			# check if customer is already created agains the self.contact_email
			customer = capkpi.db.sql(
				"""select
				distinct `tabDynamic Link`.link_name as customer
				from
					`tabContact`,
					`tabDynamic Link`
				where `tabContact`.email_id='{0}'
				and
					`tabContact`.name=`tabDynamic Link`.parent
				and
					ifnull(`tabDynamic Link`.link_name, '')<>''
				and
					`tabDynamic Link`.link_doctype='Customer'
			""".format(
					self.contact_email
				),
				as_dict=True,
			)
			if customer and customer[0].customer:
				self.party_name = customer[0].customer
				self.opportunity_from = "Customer"
				return

			lead_name = capkpi.db.get_value("Lead", {"email_id": self.contact_email})
			if not lead_name:
				sender_name = get_fullname(self.contact_email)
				if sender_name == self.contact_email:
					sender_name = None

				if not sender_name and ("@" in self.contact_email):
					email_name = self.contact_email.split("@")[0]

					email_split = email_name.split(".")
					sender_name = ""
					for s in email_split:
						sender_name += s.capitalize() + " "

				lead = capkpi.get_doc(
					{"doctype": "Lead", "email_id": self.contact_email, "lead_name": sender_name or "Unknown"}
				)

				lead.flags.ignore_email_validation = True
				lead.insert(ignore_permissions=True)
				lead_name = lead.name

			self.opportunity_from = "Lead"
			self.party_name = lead_name

	@capkpi.whitelist()
	def declare_enquiry_lost(self, lost_reasons_list, detailed_reason=None):
		if not self.has_active_quotation():
			capkpi.db.set(self, "status", "Lost")

			if detailed_reason:
				capkpi.db.set(self, "order_lost_reason", detailed_reason)

			for reason in lost_reasons_list:
				self.append("lost_reasons", reason)

			self.save()

		else:
			capkpi.throw(_("Cannot declare as lost, because Quotation has been made."))

	def on_trash(self):
		self.delete_events()

	def has_active_quotation(self):
		if not self.with_items:
			return capkpi.get_all(
				"Quotation",
				{"opportunity": self.name, "status": ("not in", ["Lost", "Closed"]), "docstatus": 1},
				"name",
			)
		else:
			return capkpi.db.sql(
				"""
				select q.name
				from `tabQuotation` q, `tabQuotation Item` qi
				where q.name = qi.parent and q.docstatus=1 and qi.prevdoc_docname =%s
				and q.status not in ('Lost', 'Closed')""",
				self.name,
			)

	def has_ordered_quotation(self):
		if not self.with_items:
			return capkpi.get_all(
				"Quotation", {"opportunity": self.name, "status": "Ordered", "docstatus": 1}, "name"
			)
		else:
			return capkpi.db.sql(
				"""
				select q.name
				from `tabQuotation` q, `tabQuotation Item` qi
				where q.name = qi.parent and q.docstatus=1 and qi.prevdoc_docname =%s
				and q.status = 'Ordered'""",
				self.name,
			)

	def has_lost_quotation(self):
		lost_quotation = capkpi.db.sql(
			"""
			select name
			from `tabQuotation`
			where docstatus=1
				and opportunity =%s and status = 'Lost'
			""",
			self.name,
		)
		if lost_quotation:
			if self.has_active_quotation():
				return False
			return True

	def validate_cust_name(self):
		if self.party_name and self.opportunity_from == "Customer":
			self.customer_name = capkpi.db.get_value("Customer", self.party_name, "customer_name")
		elif self.party_name and self.opportunity_from == "Lead":
			lead_name, company_name = capkpi.db.get_value(
				"Lead", self.party_name, ["lead_name", "company_name"]
			)
			self.customer_name = company_name or lead_name

	def on_update(self):
		self.add_calendar_event()

	def add_calendar_event(self, opts=None, force=False):
		if not opts:
			opts = capkpi._dict()

		opts.description = ""
		opts.contact_date = self.contact_date

		if self.party_name and self.opportunity_from == "Customer":
			if self.contact_person:
				opts.description = f"Contact {self.contact_person}"
			else:
				opts.description = f"Contact customer {self.party_name}"
		elif self.party_name and self.opportunity_from == "Lead":
			if self.contact_display:
				opts.description = f"Contact {self.contact_display}"
			else:
				opts.description = f"Contact lead {self.party_name}"

		opts.subject = opts.description
		opts.description += f". By : {self.contact_by}"

		if self.to_discuss:
			opts.description += f" To Discuss : {capkpi.render_template(self.to_discuss, {'doc': self})}"

		super(Opportunity, self).add_calendar_event(opts, force)

	def validate_item_details(self):
		if not self.get("items"):
			return

		# set missing values
		item_fields = ("item_name", "description", "item_group", "brand")

		for d in self.items:
			if not d.item_code:
				continue

			item = capkpi.db.get_value("Item", d.item_code, item_fields, as_dict=True)
			for key in item_fields:
				if not d.get(key):
					d.set(key, item.get(key))


@capkpi.whitelist()
def get_item_details(item_code):
	item = capkpi.db.sql(
		"""select item_name, stock_uom, image, description, item_group, brand
		from `tabItem` where name = %s""",
		item_code,
		as_dict=1,
	)
	return {
		"item_name": item and item[0]["item_name"] or "",
		"uom": item and item[0]["stock_uom"] or "",
		"description": item and item[0]["description"] or "",
		"image": item and item[0]["image"] or "",
		"item_group": item and item[0]["item_group"] or "",
		"brand": item and item[0]["brand"] or "",
	}


@capkpi.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		from erp.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = capkpi.get_doc(target)

		company_currency = capkpi.get_cached_value("Company", quotation.company, "default_currency")

		if quotation.quotation_to == "Customer" and quotation.party_name:
			party_account_currency = get_party_account_currency(
				"Customer", quotation.party_name, quotation.company
			)
		else:
			party_account_currency = company_currency

		quotation.currency = party_account_currency or company_currency

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		if not source.with_items:
			quotation.opportunity = source.name

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Quotation",
				"field_map": {
					"opportunity_from": "quotation_to",
					"name": "enq_no",
				},
			},
			"Opportunity Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					"uom": "stock_uom",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist


@capkpi.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.conversion_factor = 1.0

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {"doctype": "Request for Quotation"},
			"Opportunity Item": {
				"doctype": "Request for Quotation Item",
				"field_map": [["name", "opportunity_item"], ["parent", "opportunity"], ["uom", "uom"]],
				"postprocess": update_item,
			},
		},
		target_doc,
	)

	return doclist


@capkpi.whitelist()
def make_customer(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.opportunity_name = source.name

		if source.opportunity_from == "Lead":
			target.lead_name = source.party_name

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Customer",
				"field_map": {"currency": "default_currency", "customer_name": "customer_name"},
			}
		},
		target_doc,
		set_missing_values,
	)

	return doclist


@capkpi.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {"doctype": "Supplier Quotation", "field_map": {"name": "opportunity"}},
			"Opportunity Item": {"doctype": "Supplier Quotation Item", "field_map": {"uom": "stock_uom"}},
		},
		target_doc,
	)

	return doclist


@capkpi.whitelist()
def set_multiple_status(names, status):
	names = json.loads(names)
	for name in names:
		opp = capkpi.get_doc("Opportunity", name)
		opp.status = status
		opp.save()


def auto_close_opportunity():
	"""auto close the `Replied` Opportunities after 7 days"""
	auto_close_after_days = (
		capkpi.db.get_single_value("Selling Settings", "close_opportunity_after_days") or 15
	)

	opportunities = capkpi.db.sql(
		""" select name from tabOpportunity where status='Replied' and
		modified<DATE_SUB(CURDATE(), INTERVAL %s DAY) """,
		(auto_close_after_days),
		as_dict=True,
	)

	for opportunity in opportunities:
		doc = capkpi.get_doc("Opportunity", opportunity.get("name"))
		doc.status = "Closed"
		doc.flags.ignore_permissions = True
		doc.flags.ignore_mandatory = True
		doc.save()


@capkpi.whitelist()
def make_opportunity_from_communication(communication, company, ignore_communication_links=False):
	from erp.crm.doctype.lead.lead import make_lead_from_communication

	doc = capkpi.get_doc("Communication", communication)

	lead = doc.reference_name if doc.reference_doctype == "Lead" else None
	if not lead:
		lead = make_lead_from_communication(communication, ignore_communication_links=True)

	opportunity_from = "Lead"

	opportunity = capkpi.get_doc(
		{
			"doctype": "Opportunity",
			"company": company,
			"opportunity_from": opportunity_from,
			"party_name": lead,
		}
	).insert(ignore_permissions=True)

	link_communication_to_document(doc, "Opportunity", opportunity.name, ignore_communication_links)

	return opportunity.name


@capkpi.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from capkpi.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Opportunity", filters)

	data = capkpi.db.sql(
		"""
		select
			distinct `tabOpportunity`.name, `tabOpportunity`.customer_name, `tabOpportunity`.opportunity_amount,
			`tabOpportunity`.title, `tabOpportunity`.contact_date
		from
			`tabOpportunity`
		where
			(`tabOpportunity`.contact_date between %(start)s and %(end)s)
			{conditions}
		""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)
	return data
