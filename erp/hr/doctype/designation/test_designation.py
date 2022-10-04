# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi

# test_records = capkpi.get_test_records('Designation')


def create_designation(**args):
	args = capkpi._dict(args)
	if capkpi.db.exists("Designation", args.designation_name or "_Test designation"):
		return capkpi.get_doc("Designation", args.designation_name or "_Test designation")

	designation = capkpi.get_doc(
		{
			"doctype": "Designation",
			"designation_name": args.designation_name or "_Test designation",
			"description": args.description or "_Test description",
		}
	)
	designation.save()
	return designation
