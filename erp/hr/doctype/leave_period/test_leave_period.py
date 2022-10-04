# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

import erp

test_dependencies = ["Employee", "Leave Type", "Leave Policy"]


class TestLeavePeriod(unittest.TestCase):
	pass


def create_leave_period(from_date, to_date, company=None):
	leave_period = capkpi.db.get_value(
		"Leave Period",
		dict(
			company=company or erp.get_default_company(),
			from_date=from_date,
			to_date=to_date,
			is_active=1,
		),
		"name",
	)
	if leave_period:
		return capkpi.get_doc("Leave Period", leave_period)

	leave_period = capkpi.get_doc(
		{
			"doctype": "Leave Period",
			"company": company or erp.get_default_company(),
			"from_date": from_date,
			"to_date": to_date,
			"is_active": 1,
		}
	).insert()
	return leave_period
