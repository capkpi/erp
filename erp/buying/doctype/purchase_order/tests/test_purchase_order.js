QUnit.module('Buying');

QUnit.test("test: purchase order", function(assert) {
	assert.expect(16);
	let done = assert.async();

	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Purchase Order', [
				{supplier: 'Test Supplier'},
				{is_subcontracted: 'No'},
				{currency: 'INR'},
				{items: [
					[
						{"item_code": 'Test Product 4'},
						{"schedule_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 2)},
						{"expected_delivery_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 5)},
						{"qty": 5},
						{"uom": 'Unit'},
						{"rate": 100},
						{"warehouse": 'Stores - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
					],
					[
						{"item_code": 'Test Product 1'},
						{"schedule_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 1)},
						{"expected_delivery_date": capkpi.datetime.add_days(capkpi.datetime.now_date(), 5)},
						{"qty": 2},
						{"uom": 'Unit'},
						{"rate": 100},
						{"warehouse": 'Stores - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
					]
				]},

				{tc_name: 'Test Term 1'},
				{terms: 'This is a term.'}
			]);
		},

		() => {
			// Get supplier details
			assert.ok(cur_frm.doc.supplier_name == 'Test Supplier', "Supplier name correct");
			assert.ok(cur_frm.doc.schedule_date == capkpi.datetime.add_days(capkpi.datetime.now_date(), 1), "Schedule Date correct");
			assert.ok(cur_frm.doc.contact_email == 'test@supplier.com', "Contact email correct");
			// Get item details
			assert.ok(cur_frm.doc.items[0].item_name == 'Test Product 4', "Item name correct");
			assert.ok(cur_frm.doc.items[0].description == 'Test Product 4', "Description correct");
			assert.ok(cur_frm.doc.items[0].qty == 5, "Quantity correct");
			assert.ok(cur_frm.doc.items[0].schedule_date == capkpi.datetime.add_days(capkpi.datetime.now_date(), 2), "Schedule Date correct");

			assert.ok(cur_frm.doc.items[1].item_name == 'Test Product 1', "Item name correct");
			assert.ok(cur_frm.doc.items[1].description == 'Test Product 1', "Description correct");
			assert.ok(cur_frm.doc.items[1].qty == 2, "Quantity correct");
			assert.ok(cur_frm.doc.items[1].schedule_date == cur_frm.doc.schedule_date, "Schedule Date correct");
			// Calculate total
			assert.ok(cur_frm.doc.total == 700, "Total correct");
			// Get terms
			assert.ok(cur_frm.doc.terms == 'This is a term.', "Terms correct");
		},

		() => cur_frm.print_doc(),
		() => capkpi.timeout(2),
		() => {
			assert.ok($('.btn-print-print').is(':visible'), "Print Format Available");
			assert.ok($('div > div:nth-child(5) > div > div > table > tbody > tr > td:nth-child(4) > div').text().includes('Test Product 4'), "Print Preview Works");
		},

		() => cur_frm.print_doc(),
		() => capkpi.timeout(1),

		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(1),

		() => {
			assert.ok(cur_frm.doc.status == 'To Receive and Bill', "Submitted successfully");
		},

		() => done()
	]);
});
