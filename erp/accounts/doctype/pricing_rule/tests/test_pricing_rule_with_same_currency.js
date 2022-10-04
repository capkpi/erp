QUnit.module('Pricing Rule');

QUnit.test("test pricing rule with same currency", function(assert) {
	assert.expect(4);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make("Pricing Rule", [
				{title: 'Test Pricing Rule 1'},
				{apply_on: 'Item Code'},
				{item_code:'Test Product 4'},
				{selling:1},
				{min_qty:1},
				{max_qty:20},
				{valid_upto: capkpi.datetime.add_days(capkpi.defaults.get_default("year_end_date"), 1)},
				{rate_or_discount: 'Rate'},
				{rate:200},
				{currency:'USD'}

			]);
		},
		() => cur_frm.save(),
		() => capkpi.timeout(0.3),
		() => {
			assert.ok(cur_frm.doc.item_code=='Test Product 4');
		},

		() => {
			return capkpi.tests.make('Sales Order', [
				{customer: 'Test Customer 1'},
				{currency: 'USD'},
				{items: [
					[
						{'delivery_date': capkpi.datetime.add_days(capkpi.defaults.get_default("year_end_date"), 1)},
						{'qty': 5},
						{'item_code': "Test Product 4"}
					]
				]}
			]);
		},
		() => cur_frm.save(),
		() => capkpi.timeout(0.3),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].pricing_rule=='Test Pricing Rule 1', "Pricing rule correct");
			assert.ok(cur_frm.doc.items[0].price_list_rate==200, "Item rate correct");
			// get_total
			assert.ok(cur_frm.doc.total== 1000, "Total correct");
		},
		() => capkpi.timeout(0.3),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
