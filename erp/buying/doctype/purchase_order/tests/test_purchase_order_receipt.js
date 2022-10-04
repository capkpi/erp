QUnit.module('Buying');

QUnit.test("test: purchase order receipt", function(assert) {
	assert.expect(5);
	let done = assert.async();

	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Purchase Order', [
				{supplier: 'Test Supplier'},
				{is_subcontracted: 'No'},
				{buying_price_list: 'Test-Buying-USD'},
				{currency: 'USD'},
				{items: [
					[
						{"item_code": 'Test Product 1'},
						{"schedule_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 1)},
						{"expected_delivery_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 5)},
						{"qty": 5},
						{"uom": 'Unit'},
						{"rate": 100},
						{"warehouse": 'Stores - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
					]
				]},
			]);
		},

		() => {

			// Check supplier and item details
			assert.ok(cur_frm.doc.supplier_name == 'Test Supplier', "Supplier name correct");
			assert.ok(cur_frm.doc.items[0].item_name == 'Test Product 1', "Item name correct");
			assert.ok(cur_frm.doc.items[0].description == 'Test Product 1', "Description correct");
			assert.ok(cur_frm.doc.items[0].qty == 5, "Quantity correct");

		},

		() => capkpi.timeout(1),

		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),

		() => capkpi.timeout(1.5),
		() => capkpi.click_button('Close'),
		() => capkpi.timeout(0.3),

		// Make Purchase Receipt
		() => capkpi.click_button('Make'),
		() => capkpi.timeout(0.3),

		() => capkpi.click_link('Receipt'),
		() => capkpi.timeout(2),

		() => cur_frm.save(),

		// Save and submit Purchase Receipt
		() => capkpi.timeout(1),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(1),

		// View Purchase order in Stock Ledger
		() => capkpi.click_button('View'),
		() => capkpi.timeout(0.3),

		() => capkpi.click_link('Stock Ledger'),
		() => capkpi.timeout(2),
		() => {
			assert.ok($('div.slick-cell.l2.r2 > a').text().includes('Test Product 1')
				&& $('div.slick-cell.l9.r9 > div').text().includes(5), "Stock ledger entry correct");
		},
		() => done()
	]);
});
