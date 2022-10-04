// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Pick List', {
	setup: (frm) => {
		frm.set_indicator_formatter('item_code',
			function(doc) { return (doc.stock_qty === 0) ? "red" : "green"; });

		frm.custom_make_buttons = {
			'Delivery Note': 'Delivery Note',
			'Stock Entry': 'Stock Entry',
		};
		frm.set_query('parent_warehouse', () => {
			return {
				filters: {
					'is_group': 1,
					'company': frm.doc.company
				}
			};
		});
		frm.set_query('work_order', () => {
			return {
				query: 'erp.stock.doctype.pick_list.pick_list.get_pending_work_orders',
				filters: {
					'company': frm.doc.company
				}
			};
		});
		frm.set_query('material_request', () => {
			return {
				filters: {
					'material_request_type': ['=', frm.doc.purpose]
				}
			};
		});
		frm.set_query('item_code', 'locations', () => {
			return erp.queries.item({ "is_stock_item": 1 });
		});
		frm.set_query('batch_no', 'locations', (frm, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return {
				query: 'erp.controllers.queries.get_batch_no',
				filters: {
					item_code: row.item_code,
					warehouse: row.warehouse
				},
			};
		});
	},
	set_item_locations:(frm, save) => {
		if (!(frm.doc.locations && frm.doc.locations.length)) {
			capkpi.msgprint(__('Add items in the Item Locations table'));
		} else {
			frm.call('set_item_locations', {save: save});
		}
	},
	get_item_locations: (frm) => {
		// Button on the form
		frm.events.set_item_locations(frm, false);
	},
	refresh: (frm) => {
		frm.trigger('add_get_items_button');
		if (frm.doc.docstatus === 1) {
			capkpi.xcall('erp.stock.doctype.pick_list.pick_list.target_document_exists', {
				'pick_list_name': frm.doc.name,
				'purpose': frm.doc.purpose
			}).then(target_document_exists => {
				frm.set_df_property("locations", "allow_on_submit", target_document_exists ? 0 : 1);

				if (target_document_exists) return;

				frm.add_custom_button(__('Update Current Stock'), () => frm.trigger('update_pick_list_stock'));

				if (frm.doc.purpose === 'Delivery') {
					frm.add_custom_button(__('Delivery Note'), () => frm.trigger('create_delivery_note'), __('Create'));
				} else {
					frm.add_custom_button(__('Stock Entry'), () => frm.trigger('create_stock_entry'), __('Create'));
				}
			});
		}
	},
	work_order: (frm) => {
		capkpi.db.get_value('Work Order',
			frm.doc.work_order,
			['qty', 'material_transferred_for_manufacturing']
		).then(data => {
			let qty_data = data.message;
			let max = qty_data.qty - qty_data.material_transferred_for_manufacturing;
			capkpi.prompt({
				fieldtype: 'Float',
				label: __('Qty of Finished Goods Item'),
				fieldname: 'qty',
				description: __('Max: {0}', [max]),
				default: max
			}, (data) => {
				frm.set_value('for_qty', data.qty);
				if (data.qty > max) {
					capkpi.msgprint(__('Quantity must not be more than {0}', [max]));
					return;
				}
				frm.clear_table('locations');
				erp.utils.map_current_doc({
					method: 'erp.manufacturing.doctype.work_order.work_order.create_pick_list',
					target: frm,
					source_name: frm.doc.work_order
				});
			}, __('Select Quantity'), __('Get Items'));
		});
	},
	material_request: (frm) => {
		erp.utils.map_current_doc({
			method: 'erp.stock.doctype.material_request.material_request.create_pick_list',
			target: frm,
			source_name: frm.doc.material_request
		});
	},
	purpose: (frm) => {
		frm.clear_table('locations');
		frm.trigger('add_get_items_button');
	},
	create_delivery_note: (frm) => {
		capkpi.model.open_mapped_doc({
			method: 'erp.stock.doctype.pick_list.pick_list.create_delivery_note',
			frm: frm
		});

	},
	create_stock_entry: (frm) => {
		capkpi.xcall('erp.stock.doctype.pick_list.pick_list.create_stock_entry', {
			'pick_list': frm.doc,
		}).then(stock_entry => {
			capkpi.model.sync(stock_entry);
			capkpi.set_route("Form", 'Stock Entry', stock_entry.name);
		});
	},
	update_pick_list_stock: (frm) => {
		frm.events.set_item_locations(frm, true);
	},
	add_get_items_button: (frm) => {
		let purpose = frm.doc.purpose;
		if (purpose != 'Delivery' || frm.doc.docstatus !== 0) return;
		let get_query_filters = {
			docstatus: 1,
			per_delivered: ['<', 100],
			status: ['!=', ''],
			customer: frm.doc.customer
		};
		frm.get_items_btn = frm.add_custom_button(__('Get Items'), () => {
			erp.utils.map_current_doc({
				method: 'erp.selling.doctype.sales_order.sales_order.create_pick_list',
				source_doctype: 'Sales Order',
				target: frm,
				setters: {
					company: frm.doc.company,
					customer: frm.doc.customer
				},
				date_field: 'transaction_date',
				get_query_filters: get_query_filters
			});
		});
	}
});

capkpi.ui.form.on('Pick List Item', {
	item_code: (frm, cdt, cdn) => {
		let row = capkpi.get_doc(cdt, cdn);
		if (row.item_code) {
			get_item_details(row.item_code).then(data => {
				capkpi.model.set_value(cdt, cdn, 'uom', data.stock_uom);
				capkpi.model.set_value(cdt, cdn, 'stock_uom', data.stock_uom);
				capkpi.model.set_value(cdt, cdn, 'conversion_factor', 1);
			});
		}
	},
	uom: (frm, cdt, cdn) => {
		let row = capkpi.get_doc(cdt, cdn);
		if (row.uom) {
			get_item_details(row.item_code, row.uom).then(data => {
				capkpi.model.set_value(cdt, cdn, 'conversion_factor', data.conversion_factor);
			});
		}
	},
	qty: (frm, cdt, cdn) => {
		let row = capkpi.get_doc(cdt, cdn);
		capkpi.model.set_value(cdt, cdn, 'stock_qty', row.qty * row.conversion_factor);
	},
	conversion_factor: (frm, cdt, cdn) => {
		let row = capkpi.get_doc(cdt, cdn);
		capkpi.model.set_value(cdt, cdn, 'stock_qty', row.qty * row.conversion_factor);
	}
});

function get_item_details(item_code, uom=null) {
	if (item_code) {
		return capkpi.xcall('erp.stock.doctype.pick_list.pick_list.get_item_details', {
			item_code,
			uom
		});
	}
}
