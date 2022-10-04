// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.views.calendar["Training Event"] = {
	field_map: {
		"start": "start_time",
		"end": "end_time",
		"id": "name",
		"title": "event_name",
		"allDay": "allDay"
	},
	gantt: true,
	get_events_method: "capkpi.desk.calendar.get_events",
}
