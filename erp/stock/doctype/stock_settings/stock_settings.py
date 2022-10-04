# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.custom.doctype.property_setter.property_setter import make_property_setter
from capkpi.model.document import Document
from capkpi.utils import cint
from capkpi.utils.html_utils import clean_html

from erp.stock.utils import check_pending_reposting


class StockSettings(Document):
	def validate(self):
		for key in [
			"item_naming_by",
			"item_group",
			"stock_uom",
			"allow_negative_stock",
			"default_warehouse",
			"set_qty_in_transactions_based_on_serial_no_input",
		]:
			capkpi.db.set_default(key, self.get(key, ""))

		from erp.setup.doctype.naming_series.naming_series import set_by_naming_series

		set_by_naming_series(
			"Item",
			"item_code",
			self.get("item_naming_by") == "Naming Series",
			hide_name_field=True,
			make_mandatory=0,
		)

		stock_frozen_limit = 356
		submitted_stock_frozen = self.stock_frozen_upto_days or 0
		if submitted_stock_frozen > stock_frozen_limit:
			self.stock_frozen_upto_days = stock_frozen_limit
			capkpi.msgprint(
				_("`Freeze Stocks Older Than` should be smaller than %d days.") % stock_frozen_limit
			)

		# show/hide barcode field
		for name in ["barcode", "barcodes", "scan_barcode"]:
			capkpi.make_property_setter(
				{"fieldname": name, "property": "hidden", "value": 0 if self.show_barcode_field else 1},
				validate_fields_for_doctype=False,
			)

		self.validate_warehouses()
		self.cant_change_valuation_method()
		self.validate_clean_description_html()
		self.validate_pending_reposts()

	def validate_warehouses(self):
		warehouse_fields = ["default_warehouse", "sample_retention_warehouse"]
		for field in warehouse_fields:
			if capkpi.db.get_value("Warehouse", self.get(field), "is_group"):
				capkpi.throw(
					_("Group Warehouses cannot be used in transactions. Please change the value of {0}").format(
						capkpi.bold(self.meta.get_field(field).label)
					),
					title=_("Incorrect Warehouse"),
				)

	def cant_change_valuation_method(self):
		db_valuation_method = capkpi.db.get_single_value("Stock Settings", "valuation_method")

		if db_valuation_method and db_valuation_method != self.valuation_method:
			# check if there are any stock ledger entries against items
			# which does not have it's own valuation method
			sle = capkpi.db.sql(
				"""select name from `tabStock Ledger Entry` sle
				where exists(select name from tabItem
					where name=sle.item_code and (valuation_method is null or valuation_method='')) limit 1
			"""
			)

			if sle:
				capkpi.throw(
					_(
						"Can't change the valuation method, as there are transactions against some items which do not have its own valuation method"
					)
				)

	def validate_clean_description_html(self):
		if int(self.clean_description_html or 0) and not int(self.db_get("clean_description_html") or 0):
			# changed to text
			capkpi.enqueue(
				"erp.stock.doctype.stock_settings.stock_settings.clean_all_descriptions",
				now=capkpi.flags.in_test,
			)

	def validate_pending_reposts(self):
		if self.stock_frozen_upto:
			check_pending_reposting(self.stock_frozen_upto)

	def on_update(self):
		self.toggle_warehouse_field_for_inter_warehouse_transfer()

	def toggle_warehouse_field_for_inter_warehouse_transfer(self):
		make_property_setter(
			"Sales Invoice Item",
			"target_warehouse",
			"hidden",
			1 - cint(self.allow_from_dn),
			"Check",
			validate_fields_for_doctype=False,
		)
		make_property_setter(
			"Delivery Note Item",
			"target_warehouse",
			"hidden",
			1 - cint(self.allow_from_dn),
			"Check",
			validate_fields_for_doctype=False,
		)
		make_property_setter(
			"Purchase Invoice Item",
			"from_warehouse",
			"hidden",
			1 - cint(self.allow_from_pr),
			"Check",
			validate_fields_for_doctype=False,
		)
		make_property_setter(
			"Purchase Receipt Item",
			"from_warehouse",
			"hidden",
			1 - cint(self.allow_from_pr),
			"Check",
			validate_fields_for_doctype=False,
		)


def clean_all_descriptions():
	for item in capkpi.get_all("Item", ["name", "description"]):
		if item.description:
			clean_description = clean_html(item.description)
		if item.description != clean_description:
			capkpi.db.set_value("Item", item.name, "description", clean_description)
