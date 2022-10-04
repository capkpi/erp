# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("setup", "doctype", "global_defaults", force=True)
	capkpi.reload_doc("stock", "doctype", "delivery_trip")
	capkpi.reload_doc("stock", "doctype", "delivery_stop", force=True)

	for trip in capkpi.get_all("Delivery Trip"):
		trip_doc = capkpi.get_doc("Delivery Trip", trip.name)

		status = {0: "Draft", 1: "Scheduled", 2: "Cancelled"}[trip_doc.docstatus]

		if trip_doc.docstatus == 1:
			visited_stops = [stop.visited for stop in trip_doc.delivery_stops]
			if all(visited_stops):
				status = "Completed"
			elif any(visited_stops):
				status = "In Transit"

		capkpi.db.set_value("Delivery Trip", trip.name, "status", status, update_modified=False)
