// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
capkpi.provide("capkpi.desk");

capkpi.ui.form.on("Event", {
	refresh: function(frm) {
		frm.set_query('reference_doctype', "event_participants", function() {
			return {
				"filters": {
					"name": ["in", ["Contact", "Lead", "Customer", "Supplier", "Employee", "Sales Partner"]]
				}
			};
		});

		frm.add_custom_button(__('Add Leads'), function() {
			new capkpi.desk.eventParticipants(frm, "Lead");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Customers'), function() {
			new capkpi.desk.eventParticipants(frm, "Customer");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Suppliers'), function() {
			new capkpi.desk.eventParticipants(frm, "Supplier");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Employees'), function() {
			new capkpi.desk.eventParticipants(frm, "Employee");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Sales Partners'), function() {
			new capkpi.desk.eventParticipants(frm, "Sales Partners");
		}, __("Add Participants"));
	}
});
