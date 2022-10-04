QUnit.module('Buying');

QUnit.test("test: purchase order with shipping rule", function(assert) {
	assert.expect(3);
	let done = assert.async();

	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Purchase Order', [
				{supplier: 'Test Supplier'},
				{is_subcontracted: 'No'},
				{buying_price_list: 'Test-Buying-USD'},
				{currency: 'USD'},
				{"schedule_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 1)},
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

				{shipping_rule:'Two Day Shipping'}
			]);
		},

		() => {
			// Check grand total
			assert.ok(cur_frm.doc.total_taxes_and_charges == 200, "Taxes and charges correct");
			assert.ok(cur_frm.doc.grand_total == 2700, "Grand total correct");
		},

		() => capkpi.timeout(0.3),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
