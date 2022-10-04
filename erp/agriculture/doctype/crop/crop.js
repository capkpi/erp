// Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.provide("erp.crop");

capkpi.ui.form.on('Crop', {
	refresh: (frm) => {
		frm.fields_dict.materials_required.grid.set_column_disp('bom_no', false);
	}
});

capkpi.ui.form.on("BOM Item", {
	item_code: (frm, cdt, cdn) => {
		erp.crop.update_item_rate_uom(frm, cdt, cdn);
	},
	qty: (frm, cdt, cdn) => {
		erp.crop.update_item_qty_amount(frm, cdt, cdn);
	},
	rate: (frm, cdt, cdn) => {
		erp.crop.update_item_qty_amount(frm, cdt, cdn);
	}
});

erp.crop.update_item_rate_uom = function(frm, cdt, cdn) {
	let material_list = ['materials_required', 'produce', 'byproducts'];
	material_list.forEach((material) => {
		frm.doc[material].forEach((item, index) => {
			if (item.name == cdn && item.item_code){
				capkpi.call({
					method:'erp.agriculture.doctype.crop.crop.get_item_details',
					args: {
						item_code: item.item_code
					},
					callback: (r) => {
						capkpi.model.set_value('BOM Item', item.name, 'uom', r.message.uom);
						capkpi.model.set_value('BOM Item', item.name, 'rate', r.message.rate);
					}
				});
			}
		});
	});
};

erp.crop.update_item_qty_amount = function(frm, cdt, cdn) {
	let material_list = ['materials_required', 'produce', 'byproducts'];
	material_list.forEach((material) => {
		frm.doc[material].forEach((item, index) => {
			if (item.name == cdn){
				if (!capkpi.model.get_value('BOM Item', item.name, 'qty'))
					capkpi.model.set_value('BOM Item', item.name, 'qty', 1);
				capkpi.model.set_value('BOM Item', item.name, 'amount', item.qty * item.rate);
			}
		});
	});
};
