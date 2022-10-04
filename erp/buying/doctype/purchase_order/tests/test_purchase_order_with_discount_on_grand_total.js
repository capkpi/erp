QUnit.module('Buying');

QUnit.test("test: purchase order with discount on grand total", function(assert) {
	assert.expect(4);
	let done = assert.async();

	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Purchase Order', [
				{supplier: 'Test Supplier'},
				{is_subcontracted: 'No'},
				{buying_price_list: 'Test-Buying-EUR'},
				{currency: 'EUR'},
				{items: [
					[
						{"item_code": 'Test Product 4'},
						{"qty": 5},
						{"uom": 'Unit'},
						{"rate": 500 },
						{"schedule_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 1)},
						{"expected_delivery_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 5)},
						{"warehouse": 'Stores - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
					]
				]},
				{apply_discount_on: 'Grand Total'},
				{additional_discount_percentage: 10}
			]);
		},

		() => capkpi.timeout(1),

		() => {
			assert.ok(cur_frm.doc.supplier_name == 'Test Supplier', "Supplier name correct");
			assert.ok(cur_frm.doc.items[0].rate == 500, "Rate correct");
			// Calculate total
			assert.ok(cur_frm.doc.total == 2500, "Total correct");
			// Calculate grand total after discount
			assert.ok(cur_frm.doc.grand_total == 2250, "Grand total correct");
		},

		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),

		() => done()
	]);
});
