# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import capkpi
from capkpi.utils import cint

from erp.e_commerce.product_data_engine.filters import ProductFiltersBuilder
from erp.e_commerce.product_data_engine.query import ProductQuery
from erp.setup.doctype.item_group.item_group import get_child_groups_for_website


@capkpi.whitelist(allow_guest=True)
def get_product_filter_data(query_args=None):
	"""
	Returns filtered products and discount filters.
	:param query_args (dict): contains filters to get products list

	Query Args filters:
	search (str): Search Term.
	field_filters (dict): Keys include item_group, brand, etc.
	attribute_filters(dict): Keys include Color, Size, etc.
	start (int): Offset items by
	item_group (str): Valid Item Group
	from_filters (bool): Set as True to jump to page 1
	"""
	if isinstance(query_args, str):
		query_args = json.loads(query_args)

	query_args = capkpi._dict(query_args)
	if query_args:
		search = query_args.get("search")
		field_filters = query_args.get("field_filters", {})
		attribute_filters = query_args.get("attribute_filters", {})
		start = cint(query_args.start) if query_args.get("start") else 0
		item_group = query_args.get("item_group")
		from_filters = query_args.get("from_filters")
	else:
		search, attribute_filters, item_group, from_filters = None, None, None, None
		field_filters = {}
		start = 0

	# if new filter is checked, reset start to show filtered items from page 1
	if from_filters:
		start = 0

	sub_categories = []
	if item_group:
		sub_categories = get_child_groups_for_website(item_group, immediate=True)

	engine = ProductQuery()
	try:
		result = engine.query(
			attribute_filters, field_filters, search_term=search, start=start, item_group=item_group
		)
	except Exception:
		traceback = capkpi.get_traceback()
		capkpi.log_error(traceback, capkpi._("Product Engine Error"))
		return {"exc": "Something went wrong!"}

	# discount filter data
	filters = {}
	discounts = result["discounts"]

	if discounts:
		filter_engine = ProductFiltersBuilder()
		filters["discount_filters"] = filter_engine.get_discount_filters(discounts)

	return {
		"items": result["items"] or [],
		"filters": filters,
		"settings": engine.settings,
		"sub_categories": sub_categories,
		"items_count": result["items_count"],
	}


@capkpi.whitelist(allow_guest=True)
def get_guest_redirect_on_action():
	return capkpi.db.get_single_value("E Commerce Settings", "redirect_on_action")
