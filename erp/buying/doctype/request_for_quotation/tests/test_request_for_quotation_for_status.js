QUnit.module('buying');

QUnit.test("Test: Request for Quotation", function (assert) {
	assert.expect(5);
	let done = assert.async();
	let rfq_name = "";

	capkpi.run_serially([
		// Go to RFQ list
		() => capkpi.set_route("List", "Request for Quotation"),
		// Create a new RFQ
		() => capkpi.new_doc("Request for Quotation"),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("transaction_date", "04-04-2017"),
		() => cur_frm.set_value("company", "For Testing"),
		// Add Suppliers
		() => {
			cur_frm.fields_dict.suppliers.grid.grid_rows[0].toggle_view();
		},
		() => capkpi.timeout(1),
		() => {
			cur_frm.fields_dict.suppliers.grid.grid_rows[0].doc.supplier = "_Test Supplier";
			capkpi.click_check('Send Email');
			cur_frm.cur_grid.frm.script_manager.trigger('supplier');
		},
		() => capkpi.timeout(1),
		() => {
			cur_frm.cur_grid.toggle_view();
		},
		() => capkpi.timeout(1),
		() => capkpi.click_button('Add Row',0),
		() => capkpi.timeout(1),
		() => {
			cur_frm.fields_dict.suppliers.grid.grid_rows[1].toggle_view();
		},
		() => capkpi.timeout(1),
		() => {
			cur_frm.fields_dict.suppliers.grid.grid_rows[1].doc.supplier = "_Test Supplier 1";
			capkpi.click_check('Send Email');
			cur_frm.cur_grid.frm.script_manager.trigger('supplier');
		},
		() => capkpi.timeout(1),
		() => {
			cur_frm.cur_grid.toggle_view();
		},
		() => capkpi.timeout(1),
		// Add Item
		() => {
			cur_frm.fields_dict.items.grid.grid_rows[0].toggle_view();
		},
		() => capkpi.timeout(1),
		() => {
			cur_frm.fields_dict.items.grid.grid_rows[0].doc.item_code = "_Test Item";
			capkpi.set_control('item_code',"_Test Item");
			capkpi.set_control('qty',5);
			capkpi.set_control('schedule_date', "05-05-2017");
			cur_frm.cur_grid.frm.script_manager.trigger('supplier');
		},
		() => capkpi.timeout(2),
		() => {
			cur_frm.cur_grid.toggle_view();
		},
		() => capkpi.timeout(2),
		() => {
			cur_frm.fields_dict.items.grid.grid_rows[0].doc.warehouse = "_Test Warehouse - FT";
		},
		() => capkpi.click_button('Save'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Submit'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Menu'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Reload'),
		() => capkpi.timeout(1),
		() => {
			assert.equal(cur_frm.doc.docstatus, 1);
			rfq_name = cur_frm.doc.name;
			assert.ok(cur_frm.fields_dict.suppliers.grid.grid_rows[0].doc.quote_status == "Pending");
			assert.ok(cur_frm.fields_dict.suppliers.grid.grid_rows[1].doc.quote_status == "Pending");
		},
		() => {
			cur_frm.fields_dict.suppliers.grid.grid_rows[0].toggle_view();
		},
		() => capkpi.timeout(1),
		() => capkpi.timeout(1),
		() => {
			cur_frm.cur_grid.toggle_view();
		},
		() => capkpi.click_button('Update'),
		() => capkpi.timeout(1),

		() => capkpi.click_button('Supplier Quotation'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Make'),
		() => capkpi.timeout(1),
		() => {
			capkpi.set_control('supplier',"_Test Supplier 1");
		},
		() => capkpi.timeout(1),
		() => capkpi.click_button('Make Supplier Quotation'),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("company", "For Testing"),
		() => cur_frm.fields_dict.items.grid.grid_rows[0].doc.rate = 4.99,
		() => capkpi.timeout(1),
		() => capkpi.click_button('Save'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Submit'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(1),
		() => capkpi.set_route("List", "Request for Quotation"),
		() => capkpi.timeout(2),
		() => capkpi.set_route("List", "Request for Quotation"),
		() => capkpi.timeout(2),
		() => capkpi.click_link(rfq_name),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Menu'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Reload'),
		() => capkpi.timeout(1),
		() => {
			assert.ok(cur_frm.fields_dict.suppliers.grid.grid_rows[1].doc.quote_status == "Received");
		},
		() => done()
	]);
});
