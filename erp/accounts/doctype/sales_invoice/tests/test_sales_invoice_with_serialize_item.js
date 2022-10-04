QUnit.module('Sales Invoice');

QUnit.test("test sales Invoice with serialize item", function(assert) {
	assert.expect(5);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Sales Invoice', [
				{customer: 'Test Customer 1'},
				{items: [
					[
						{'qty': 2},
						{'item_code': 'Test Product 4'},
					]
				]},
				{update_stock:1},
				{customer_address: 'Test1-Billing'},
				{shipping_address_name: 'Test1-Shipping'},
				{contact_person: 'Contact 1-Test Customer 1'},
				{taxes_and_charges: 'TEST In State GST - FT'},
				{tc_name: 'Test Term 1'},
				{terms: 'This is Test'}
			]);
		},
		() => cur_frm.save(),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].item_name=='Test Product 4', "Item name correct");
			// get tax details
			assert.ok(cur_frm.doc.taxes_and_charges=='TEST In State GST - FT', "Tax details correct");
			// get tax account head details
			assert.ok(cur_frm.doc.taxes[0].account_head=='CGST - '+capkpi.get_abbr(capkpi.defaults.get_default('Company')), " Account Head abbr correct");
			// get batch number
			assert.ok(cur_frm.doc.items[0].batch_no=='TEST-BATCH-001', " Batch Details correct");
			// grand_total Calculated
			assert.ok(cur_frm.doc.grand_total==218, "Grad Total correct");

		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
