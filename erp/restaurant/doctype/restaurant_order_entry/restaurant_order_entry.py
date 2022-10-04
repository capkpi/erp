# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi import _
from capkpi.model.document import Document

from erp.controllers.queries import item_query


class RestaurantOrderEntry(Document):
	pass


@capkpi.whitelist()
def get_invoice(table):
	"""returns the active invoice linked to the given table"""
	invoice_name = capkpi.get_value("Sales Invoice", dict(restaurant_table=table, docstatus=0))
	restaurant, menu_name = get_restaurant_and_menu_name(table)
	if invoice_name:
		invoice = capkpi.get_doc("Sales Invoice", invoice_name)
	else:
		invoice = capkpi.new_doc("Sales Invoice")
		invoice.naming_series = capkpi.db.get_value("Restaurant", restaurant, "invoice_series_prefix")
		invoice.is_pos = 1
		default_customer = capkpi.db.get_value("Restaurant", restaurant, "default_customer")
		if not default_customer:
			capkpi.throw(_("Please set default customer in Restaurant Settings"))
		invoice.customer = default_customer

	invoice.taxes_and_charges = capkpi.db.get_value("Restaurant", restaurant, "default_tax_template")
	invoice.selling_price_list = capkpi.db.get_value(
		"Price List", dict(restaurant_menu=menu_name, enabled=1)
	)

	return invoice


@capkpi.whitelist()
def sync(table, items):
	"""Sync the sales order related to the table"""
	invoice = get_invoice(table)
	items = json.loads(items)

	invoice.items = []
	invoice.restaurant_table = table
	for d in items:
		invoice.append("items", dict(item_code=d.get("item"), qty=d.get("qty")))

	invoice.save()
	return invoice.as_dict()


@capkpi.whitelist()
def make_invoice(table, customer, mode_of_payment):
	"""Make table based on Sales Order"""
	restaurant, menu = get_restaurant_and_menu_name(table)
	invoice = get_invoice(table)
	invoice.customer = customer
	invoice.restaurant = restaurant
	invoice.calculate_taxes_and_totals()
	invoice.append("payments", dict(mode_of_payment=mode_of_payment, amount=invoice.grand_total))
	invoice.save()
	invoice.submit()

	capkpi.msgprint(_("Invoice Created"), indicator="green", alert=True)

	return invoice.name


@capkpi.whitelist()
def item_query_restaurant(
	doctype="Item", txt="", searchfield="name", start=0, page_len=20, filters=None, as_dict=False
):
	"""Return items that are selected in active menu of the restaurant"""
	restaurant, menu = get_restaurant_and_menu_name(filters["table"])
	items = capkpi.db.get_all("Restaurant Menu Item", ["item"], dict(parent=menu))
	del filters["table"]
	filters["name"] = ("in", [d.item for d in items])

	return item_query("Item", txt, searchfield, start, page_len, filters, as_dict)


def get_restaurant_and_menu_name(table):
	if not table:
		capkpi.throw(_("Please select a table"))

	restaurant = capkpi.db.get_value("Restaurant Table", table, "restaurant")
	menu = capkpi.db.get_value("Restaurant", restaurant, "active_menu")

	if not menu:
		capkpi.throw(_("Please set an active menu for Restaurant {0}").format(restaurant))

	return restaurant, menu
