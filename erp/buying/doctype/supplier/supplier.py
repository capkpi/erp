# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
import capkpi.defaults
from capkpi import _, msgprint
from capkpi.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from capkpi.model.naming import set_name_by_naming_series, set_name_from_naming_options

from erp.accounts.party import (  # noqa
	get_dashboard_info,
	get_timeline_data,
	validate_party_accounts,
)
from erp.utilities.transaction_base import TransactionBase


class Supplier(TransactionBase):
	def get_feed(self):
		return self.supplier_name

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
		self.load_dashboard_info()

	def before_save(self):
		if not self.on_hold:
			self.hold_type = ""
			self.release_date = ""
		elif self.on_hold and not self.hold_type:
			self.hold_type = "All"

	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name)
		self.set_onload("dashboard_info", info)

	def autoname(self):
		supp_master_name = capkpi.defaults.get_global_default("supp_master_name")
		if supp_master_name == "Supplier Name":
			self.name = self.supplier_name
		elif supp_master_name == "Naming Series":
			set_name_by_naming_series(self)
		else:
			self.name = set_name_from_naming_options(capkpi.get_meta(self.doctype).autoname, self)

	def on_update(self):
		if not self.naming_series:
			self.naming_series = ""

		self.create_primary_contact()
		self.create_primary_address()

	def validate(self):
		self.flags.is_new_doc = self.is_new()

		# validation for Naming Series mandatory field...
		if capkpi.defaults.get_global_default("supp_master_name") == "Naming Series":
			if not self.naming_series:
				msgprint(_("Series is mandatory"), raise_exception=1)

		validate_party_accounts(self)
		self.validate_internal_supplier()

	@capkpi.whitelist()
	def get_supplier_group_details(self):
		doc = capkpi.get_doc("Supplier Group", self.supplier_group)
		self.payment_terms = ""
		self.accounts = []

		if doc.accounts:
			for account in doc.accounts:
				child = self.append("accounts")
				child.company = account.company
				child.account = account.account

		if doc.payment_terms:
			self.payment_terms = doc.payment_terms

		self.save()

	def validate_internal_supplier(self):
		if not self.is_internal_supplier:
			self.represents_company = ""

		internal_supplier = capkpi.db.get_value(
			"Supplier",
			{
				"is_internal_supplier": 1,
				"represents_company": self.represents_company,
				"name": ("!=", self.name),
			},
			"name",
		)

		if internal_supplier:
			capkpi.throw(
				_("Internal Supplier for company {0} already exists").format(
					capkpi.bold(self.represents_company)
				)
			)

	def create_primary_contact(self):
		from erp.selling.doctype.customer.customer import make_contact

		if not self.supplier_primary_contact:
			if self.mobile_no or self.email_id:
				contact = make_contact(self)
				self.db_set("supplier_primary_contact", contact.name)
				self.db_set("mobile_no", self.mobile_no)
				self.db_set("email_id", self.email_id)

	def create_primary_address(self):
		from capkpi.contacts.doctype.address.address import get_address_display

		from erp.selling.doctype.customer.customer import make_address

		if self.flags.is_new_doc and self.get("address_line1"):
			address = make_address(self)
			address_display = get_address_display(address.name)

			self.db_set("supplier_primary_address", address.name)
			self.db_set("primary_address", address_display)

	def on_trash(self):
		if self.supplier_primary_contact:
			capkpi.db.sql(
				"""
				UPDATE `tabSupplier`
				SET
					supplier_primary_contact=null,
					supplier_primary_address=null,
					mobile_no=null,
					email_id=null,
					primary_address=null
				WHERE name=%(name)s""",
				{"name": self.name},
			)

		delete_contact_and_address("Supplier", self.name)

	def after_rename(self, olddn, newdn, merge=False):
		if capkpi.defaults.get_global_default("supp_master_name") == "Supplier Name":
			capkpi.db.set(self, "supplier_name", newdn)

	def create_onboarding_docs(self, args):
		company = capkpi.defaults.get_defaults().get("company") or capkpi.db.get_single_value(
			"Global Defaults", "default_company"
		)

		for i in range(1, args.get("max_count")):
			supplier = args.get("supplier_name_" + str(i))
			if supplier:
				try:
					doc = capkpi.get_doc(
						{
							"doctype": self.doctype,
							"supplier_name": supplier,
							"supplier_group": _("Local"),
							"company": company,
						}
					).insert()

					if args.get("supplier_email_" + str(i)):
						from erp.selling.doctype.customer.customer import create_contact

						create_contact(supplier, "Supplier", doc.name, args.get("supplier_email_" + str(i)))
				except capkpi.NameError:
					pass


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_supplier_primary_contact(doctype, txt, searchfield, start, page_len, filters):
	supplier = filters.get("supplier")
	return capkpi.db.sql(
		"""
		SELECT
			`tabContact`.name from `tabContact`,
			`tabDynamic Link`
		WHERE
			`tabContact`.name = `tabDynamic Link`.parent
			and `tabDynamic Link`.link_name = %(supplier)s
			and `tabDynamic Link`.link_doctype = 'Supplier'
			and `tabContact`.name like %(txt)s
		""",
		{"supplier": supplier, "txt": "%%%s%%" % txt},
	)
