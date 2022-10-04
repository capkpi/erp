import json

import capkpi
from capkpi.model.naming import make_autoname
from six import iteritems


def execute():
	if "tax_type" not in capkpi.db.get_table_columns("Item Tax"):
		return
	old_item_taxes = {}
	item_tax_templates = {}

	capkpi.reload_doc("accounts", "doctype", "item_tax_template_detail", force=1)
	capkpi.reload_doc("accounts", "doctype", "item_tax_template", force=1)
	existing_templates = capkpi.db.sql(
		"""select template.name, details.tax_type, details.tax_rate
		from `tabItem Tax Template` template, `tabItem Tax Template Detail` details
		where details.parent=template.name
		""",
		as_dict=1,
	)

	if len(existing_templates):
		for d in existing_templates:
			item_tax_templates.setdefault(d.name, {})
			item_tax_templates[d.name][d.tax_type] = d.tax_rate

	for d in capkpi.db.sql(
		"""select parent as item_code, tax_type, tax_rate from `tabItem Tax`""", as_dict=1
	):
		old_item_taxes.setdefault(d.item_code, [])
		old_item_taxes[d.item_code].append(d)

	capkpi.reload_doc("stock", "doctype", "item", force=1)
	capkpi.reload_doc("stock", "doctype", "item_tax", force=1)
	capkpi.reload_doc("selling", "doctype", "quotation_item", force=1)
	capkpi.reload_doc("selling", "doctype", "sales_order_item", force=1)
	capkpi.reload_doc("stock", "doctype", "delivery_note_item", force=1)
	capkpi.reload_doc("accounts", "doctype", "sales_invoice_item", force=1)
	capkpi.reload_doc("buying", "doctype", "supplier_quotation_item", force=1)
	capkpi.reload_doc("buying", "doctype", "purchase_order_item", force=1)
	capkpi.reload_doc("stock", "doctype", "purchase_receipt_item", force=1)
	capkpi.reload_doc("accounts", "doctype", "purchase_invoice_item", force=1)
	capkpi.reload_doc("accounts", "doctype", "accounts_settings", force=1)

	capkpi.db.auto_commit_on_many_writes = True

	# for each item that have item tax rates
	for item_code in old_item_taxes.keys():
		# make current item's tax map
		item_tax_map = {}
		for d in old_item_taxes[item_code]:
			if d.tax_type not in item_tax_map:
				item_tax_map[d.tax_type] = d.tax_rate

		tax_types = []
		item_tax_template_name = get_item_tax_template(
			item_tax_templates, item_tax_map, item_code, tax_types=tax_types
		)

		# update the item tax table
		capkpi.db.sql("delete from `tabItem Tax` where parent=%s and parenttype='Item'", item_code)
		if item_tax_template_name:
			item = capkpi.get_doc("Item", item_code)
			item.set("taxes", [])
			item.append("taxes", {"item_tax_template": item_tax_template_name, "tax_category": ""})
			for d in item.taxes:
				d.db_insert()

	doctypes = [
		"Quotation",
		"Sales Order",
		"Delivery Note",
		"Sales Invoice",
		"Supplier Quotation",
		"Purchase Order",
		"Purchase Receipt",
		"Purchase Invoice",
	]

	for dt in doctypes:
		for d in capkpi.db.sql(
			"""select name, parenttype, parent, item_code, item_tax_rate from `tab{0} Item`
								where ifnull(item_tax_rate, '') not in ('', '{{}}')
								and item_tax_template is NULL""".format(
				dt
			),
			as_dict=1,
		):
			item_tax_map = json.loads(d.item_tax_rate)
			item_tax_template_name = get_item_tax_template(
				item_tax_templates, item_tax_map, d.item_code, d.parenttype, d.parent, tax_types=tax_types
			)
			capkpi.db.set_value(dt + " Item", d.name, "item_tax_template", item_tax_template_name)

	capkpi.db.auto_commit_on_many_writes = False

	settings = capkpi.get_single("Accounts Settings")
	settings.add_taxes_from_item_tax_template = 0
	settings.determine_address_tax_category_from = "Billing Address"
	settings.save()


def get_item_tax_template(
	item_tax_templates, item_tax_map, item_code, parenttype=None, parent=None, tax_types=None
):
	# search for previously created item tax template by comparing tax maps
	for template, item_tax_template_map in iteritems(item_tax_templates):
		if item_tax_map == item_tax_template_map:
			return template

	# if no item tax template found, create one
	item_tax_template = capkpi.new_doc("Item Tax Template")
	item_tax_template.title = make_autoname("Item Tax Template-.####")
	item_tax_template_name = item_tax_template.title

	for tax_type, tax_rate in iteritems(item_tax_map):
		account_details = capkpi.db.get_value(
			"Account", tax_type, ["name", "account_type", "company"], as_dict=1
		)
		if account_details:
			item_tax_template.company = account_details.company
			if not item_tax_template_name:
				# set name once company is set as name is generated from company & title
				# setting name is required to update `item_tax_templates` dict
				item_tax_template_name = item_tax_template.set_new_name()
			if account_details.account_type not in (
				"Tax",
				"Chargeable",
				"Income Account",
				"Expense Account",
				"Expenses Included In Valuation",
			):
				capkpi.db.set_value("Account", account_details.name, "account_type", "Chargeable")
		else:
			parts = tax_type.strip().split(" - ")
			account_name = " - ".join(parts[:-1])
			if not account_name:
				tax_type = None
			else:
				company = get_company(parts[-1], parenttype, parent)
				parent_account = capkpi.get_value(
					"Account", {"account_name": account_name, "company": company}, "parent_account"
				)
				if not parent_account:
					parent_account = capkpi.db.get_value(
						"Account",
						filters={"account_type": "Tax", "root_type": "Liability", "is_group": 0, "company": company},
						fieldname="parent_account",
					)
				if not parent_account:
					parent_account = capkpi.db.get_value(
						"Account",
						filters={"account_type": "Tax", "root_type": "Liability", "is_group": 1, "company": company},
					)
				filters = {
					"account_name": account_name,
					"company": company,
					"account_type": "Tax",
					"parent_account": parent_account,
				}
				tax_type = capkpi.db.get_value("Account", filters)
				if not tax_type:
					account = capkpi.new_doc("Account")
					account.update(filters)
					try:
						account.insert()
						tax_type = account.name
					except capkpi.DuplicateEntryError:
						tax_type = capkpi.db.get_value(
							"Account", {"account_name": account_name, "company": company}, "name"
						)

		account_type = capkpi.get_cached_value("Account", tax_type, "account_type")

		if tax_type and account_type in (
			"Tax",
			"Chargeable",
			"Income Account",
			"Expense Account",
			"Expenses Included In Valuation",
		):
			if tax_type not in tax_types:
				item_tax_template.append("taxes", {"tax_type": tax_type, "tax_rate": tax_rate})
				tax_types.append(tax_type)
			item_tax_templates.setdefault(item_tax_template_name, {})
			item_tax_templates[item_tax_template_name][tax_type] = tax_rate

	if item_tax_template.get("taxes"):
		item_tax_template.save()
		return item_tax_template.name


def get_company(company_abbr, parenttype=None, parent=None):
	if parenttype and parent:
		company = capkpi.get_cached_value(parenttype, parent, "company")
	else:
		company = capkpi.db.get_value("Company", filters={"abbr": company_abbr})

	if not company:
		companies = capkpi.get_all("Company")
		if len(companies) == 1:
			company = companies[0].name

	return company
