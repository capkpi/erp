// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Routing', {
	refresh: function(frm) {
		frm.trigger("display_sequence_id_column");
	},

	onload: function(frm) {
		frm.trigger("display_sequence_id_column");
	},

	display_sequence_id_column: function(frm) {
		frm.fields_dict.operations.grid.update_docfield_property(
			'sequence_id', 	'in_list_view', 1
		);
	},

	calculate_operating_cost: function(frm, child) {
		const operating_cost = flt(flt(child.hour_rate) * flt(child.time_in_mins) / 60, precision("operating_cost", child));
		capkpi.model.set_value(child.doctype, child.name, "operating_cost", operating_cost);
	}
});

capkpi.ui.form.on('BOM Operation', {
	operation: function(frm, cdt, cdn) {
		const d = locals[cdt][cdn];

		if(!d.operation) return;

		capkpi.call({
			"method": "capkpi.client.get",
			args: {
				doctype: "Operation",
				name: d.operation
			},
			callback: function (data) {
				if (data.message.description) {
					capkpi.model.set_value(d.doctype, d.name, "description", data.message.description);
				}

				if (data.message.workstation) {
					capkpi.model.set_value(d.doctype, d.name, "workstation", data.message.workstation);
				}

				frm.events.calculate_operating_cost(frm, d);
			}
		});
	},

	workstation: function(frm, cdt, cdn) {
		const d = locals[cdt][cdn];

		capkpi.call({
			"method": "capkpi.client.get",
			args: {
				doctype: "Workstation",
				name: d.workstation
			},
			callback: function (data) {
				capkpi.model.set_value(d.doctype, d.name, "hour_rate", data.message.hour_rate);
				frm.events.calculate_operating_cost(frm, d);
			}
		});
	},

	time_in_mins: function(frm, cdt, cdn) {
		const d = locals[cdt][cdn];
		frm.events.calculate_operating_cost(frm, d);
	}
});
