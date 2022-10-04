QUnit.module('stock');
QUnit.test("test: item", function (assert) {
	assert.expect(6);
	let done = assert.async();
	let keyboard_cost  = 800;
	let screen_cost  = 4000;
	let CPU_cost  = 15000;
	let scrap_cost = 100;
	let no_of_items_to_stock = 100;
	let is_stock_item = 1;
	capkpi.run_serially([
		// test item creation
		() => capkpi.set_route("List", "Item"),

		// Create a keyboard item
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Keyboard"},
				{item_group: "Products"},
				{is_stock_item: is_stock_item},
				{standard_rate: keyboard_cost},
				{opening_stock: no_of_items_to_stock},
				{default_warehouse: "Stores - FT"}
			]
		),
		() => {
			assert.ok(cur_frm.doc.item_name.includes('Keyboard'),
				'Item Keyboard created correctly');
			assert.ok(cur_frm.doc.item_code.includes('Keyboard'),
				'item_code for Keyboard set correctly');
			assert.ok(cur_frm.doc.item_group.includes('Products'),
				'item_group for Keyboard set correctly');
			assert.equal(cur_frm.doc.is_stock_item, is_stock_item,
				'is_stock_item for Keyboard set correctly');
			assert.equal(cur_frm.doc.standard_rate, keyboard_cost,
				'standard_rate for Keyboard set correctly');
			assert.equal(cur_frm.doc.opening_stock, no_of_items_to_stock,
				'opening_stock for Keyboard set correctly');
		},

		// Create a Screen item
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Screen"},
				{item_group: "Products"},
				{is_stock_item: is_stock_item},
				{standard_rate: screen_cost},
				{opening_stock: no_of_items_to_stock},
				{default_warehouse: "Stores - FT"}
			]
		),

		// Create a CPU item
		() => capkpi.tests.make(
			"Item", [
				{item_code: "CPU"},
				{item_group: "Products"},
				{is_stock_item: is_stock_item},
				{standard_rate: CPU_cost},
				{opening_stock: no_of_items_to_stock},
				{default_warehouse: "Stores - FT"}
			]
		),

		// Create a laptop item
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Laptop"},
				{item_group: "Products"},
				{default_warehouse: "Stores - FT"}
			]
		),
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Computer"},
				{item_group: "Products"},
				{is_stock_item: 0},
			]
		),

		// Create a scrap item
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Scrap item"},
				{item_group: "Products"},
				{is_stock_item: is_stock_item},
				{standard_rate: scrap_cost},
				{opening_stock: no_of_items_to_stock},
				{default_warehouse: "Stores - FT"}
			]
		),
		() => capkpi.tests.make(
			"Item", [
				{item_code: "Test Product 4"},
				{item_group: "Products"},
				{is_stock_item: 1},
				{has_batch_no: 1},
				{create_new_batch: 1},
				{uoms:
					[
						[
							{uom:"Unit"},
							{conversion_factor: 10},
						]
					]
				},
				{taxes:
					[
						[
							{tax_type:"SGST - "+capkpi.get_abbr(capkpi.defaults.get_default("Company"))},
							{tax_rate: 0},
						]
					]},
				{has_serial_no: 1},
				{standard_rate: 100},
				{opening_stock: 100},
			]
		),
		() => done()
	]);
});
