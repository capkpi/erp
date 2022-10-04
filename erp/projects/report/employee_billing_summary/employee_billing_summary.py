# Copyright (c) 2013, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi

from erp.projects.report.billing_summary import get_columns, get_data


def execute(filters=None):
	filters = capkpi._dict(filters or {})
	columns = get_columns()

	data = get_data(filters)
	return columns, data
