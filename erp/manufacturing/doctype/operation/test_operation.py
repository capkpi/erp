# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

test_records = capkpi.get_test_records("Operation")


class TestOperation(unittest.TestCase):
	pass


def make_operation(*args, **kwargs):
	args = args if args else kwargs
	if isinstance(args, tuple):
		args = args[0]

	args = capkpi._dict(args)

	if not capkpi.db.exists("Operation", args.operation):
		doc = capkpi.get_doc(
			{"doctype": "Operation", "name": args.operation, "workstation": args.workstation}
		)
		doc.insert()
		return doc

	return capkpi.get_doc("Operation", args.operation)
