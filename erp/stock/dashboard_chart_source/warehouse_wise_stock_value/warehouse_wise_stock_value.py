# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import _
from capkpi.utils.dashboard import cache_source


@capkpi.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	labels, datapoints = [], []
	filters = capkpi.parse_json(filters)

	warehouse_filters = [["is_group", "=", 0]]
	if filters and filters.get("company"):
		warehouse_filters.append(["company", "=", filters.get("company")])

	warehouses = capkpi.get_list(
		"Warehouse", pluck="name", filters=warehouse_filters, order_by="name"
	)

	warehouses = capkpi.get_list(
		"Bin",
		fields=["warehouse", "sum(stock_value) stock_value"],
		filters={"warehouse": ["IN", warehouses], "stock_value": [">", 0]},
		group_by="warehouse",
		order_by="stock_value DESC",
		limit_page_length=10,
	)

	if not warehouses:
		return []

	for warehouse in warehouses:
		labels.append(_(warehouse.get("warehouse")))
		datapoints.append(warehouse.get("stock_value"))

	return {
		"labels": labels,
		"datasets": [{"name": _("Stock Value"), "values": datapoints}],
		"type": "bar",
	}
