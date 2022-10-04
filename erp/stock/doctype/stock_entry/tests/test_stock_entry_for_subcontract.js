QUnit.module('Stock');

QUnit.test("test material Transfer to manufacture", function(assert) {
	assert.expect(3);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Stock Entry', [
				{purpose:'Send to Subcontractor'},
				{from_warehouse:'Work In Progress - '+capkpi.get_abbr(capkpi.defaults.get_default('Company'))},
				{to_warehouse:'Finished Goods - '+capkpi.get_abbr(capkpi.defaults.get_default('Company'))},
				{items: [
					[
						{'item_code': 'Test Product 1'},
						{'qty': 1},
					]
				]},
			]);
		},
		() => cur_frm.save(),
		() => capkpi.click_button('Update Rate and Availability'),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].item_name=='Test Product 1', "Item name correct");
			assert.ok(cur_frm.doc.total_outgoing_value==100, " Outgoing Value correct");
			assert.ok(cur_frm.doc.total_incoming_value==100, " Incoming Value correct");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
