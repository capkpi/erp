QUnit.module('Stock');

QUnit.test("test material request for issue", function(assert) {
	assert.expect(1);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Material Request', [
				{material_request_type:'Material Issue'},
				{items: [
					[
						{'schedule_date':  capkpi.datetime.add_days(capkpi.datetime.nowdate(), 5)},
						{'qty': 5},
						{'item_code': 'Test Product 1'},
					]
				]},
			]);
		},
		() => cur_frm.save(),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.items[0].item_name=='Test Product 1', "Item name correct");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
