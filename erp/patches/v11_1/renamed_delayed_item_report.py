# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	for report in ["Delayed Order Item Summary", "Delayed Order Summary"]:
		if capkpi.db.exists("Report", report):
			capkpi.delete_doc("Report", report)
