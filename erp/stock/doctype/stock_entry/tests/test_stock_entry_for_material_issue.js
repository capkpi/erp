QUnit.module('Stock');

QUnit.test("test material request", function(assert) {
	assert.expect(2);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Stock Entry', [
				{from_warehouse:'Stores - '+capkpi.get_abbr(capkpi.defaults.get_default('Company'))},
				{items: [
					[
						{'item_code': 'Test Product 1'},
						{'qty': 5},
					]
				]},
			]);
		},
		() => cur_frm.save(),
		() => capkpi.click_button('Update Rate and Availability'),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].item_name=='Test Product 1', "Item name correct");
			assert.ok(cur_frm.doc.total_outgoing_value==500, " Outgoing Value correct");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
