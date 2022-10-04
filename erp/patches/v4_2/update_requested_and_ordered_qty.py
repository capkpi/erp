# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	from erp.stock.stock_balance import get_indented_qty, get_ordered_qty, update_bin_qty

	count = 0
	for item_code, warehouse in capkpi.db.sql(
		"""select distinct item_code, warehouse from
		(select item_code, warehouse from tabBin
		union
		select item_code, warehouse from `tabStock Ledger Entry`) a"""
	):
		try:
			if not (item_code and warehouse):
				continue
			count += 1
			update_bin_qty(
				item_code,
				warehouse,
				{
					"indented_qty": get_indented_qty(item_code, warehouse),
					"ordered_qty": get_ordered_qty(item_code, warehouse),
				},
			)
			if count % 200 == 0:
				capkpi.db.commit()
		except Exception:
			capkpi.db.rollback()
