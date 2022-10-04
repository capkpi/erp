QUnit.module('Buying');

QUnit.test("test: supplier quotation", function(assert) {
	assert.expect(11);
	let done = assert.async();
	let date;

	capkpi.run_serially([
		() => {
			date = capkpi.datetime.add_days(capkpi.datetime.now_date(), 10);
			return capkpi.tests.make('Supplier Quotation', [
				{supplier: 'Test Supplier'},
				{transaction_date: date},
				{currency: 'INR'},
				{items: [
					[
						{"item_code": 'Test Product 4'},
						{"qty": 5},
						{"uom": 'Unit'},
						{"rate": 200},
						{"warehouse": 'All Warehouses - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
					]
				]},
				{apply_discount_on: 'Grand Total'},
				{additional_discount_percentage: 10},
				{tc_name: 'Test Term 1'},
				{terms: 'This is a term'}
			]);
		},
		() => capkpi.timeout(3),
		() => {
			// Get Supplier details
			assert.ok(cur_frm.doc.supplier == 'Test Supplier', "Supplier correct");
			assert.ok(cur_frm.doc.company == cur_frm.doc.company, "Company correct");
			// Get Contact details
			assert.ok(cur_frm.doc.contact_person == 'Contact 3-Test Supplier', "Conatct correct");
			assert.ok(cur_frm.doc.contact_email == 'test@supplier.com', "Email correct");
			// Get uom
			assert.ok(cur_frm.doc.items[0].uom == 'Unit', "Multi uom correct");
			assert.ok(cur_frm.doc.total ==  1000, "Total correct");
			// Calculate total after discount
			assert.ok(cur_frm.doc.grand_total ==  900, "Grand total correct");
			// Get terms
			assert.ok(cur_frm.doc.tc_name == 'Test Term 1', "Terms correct");
		},

		() => cur_frm.print_doc(),
		() => capkpi.timeout(2),
		() => {
			assert.ok($('.btn-print-print').is(':visible'), "Print Format Available");
			assert.ok($("table > tbody > tr > td:nth-child(3) > div").text().includes("Test Product 4"), "Print Preview Works As Expected");
		},
		() => cur_frm.print_doc(),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Get items from'),
		() => capkpi.timeout(0.3),
		() => capkpi.click_link('Material Request'),
		() => capkpi.timeout(0.3),
		() => capkpi.click_button('Get Items'),
		() => capkpi.timeout(1),
		() => {
			// Get item from Material Requests
			assert.ok(cur_frm.doc.items[1].item_name == 'Test Product 1', "Getting items from material requests work");
		},

		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),

		() => done()
	]);
});
