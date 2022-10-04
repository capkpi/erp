QUnit.test("test: opportunity", function (assert) {
	assert.expect(8);
	let done = assert.async();
	capkpi.run_serially([
		() => capkpi.set_route('List', 'Opportunity'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('New'),
		() => capkpi.timeout(1),
		() => cur_frm.set_value('opportunity_from', 'Customer'),
		() => cur_frm.set_value('customer', 'Test Customer 1'),

		// check items
		() => cur_frm.set_value('with_items', 1),
		() => capkpi.tests.set_grid_values(cur_frm, 'items', [
			[
				{item_code:'Test Product 1'},
				{qty: 4}
			]
		]),
		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => {
			assert.notOk(cur_frm.is_new(), 'saved');
			capkpi.opportunity_name = cur_frm.doc.name;
		},

		// close and re-open
		() => capkpi.click_button('Close'),
		() => capkpi.timeout(1),
		() => assert.equal(cur_frm.doc.status, 'Closed',
			'closed'),

		() => capkpi.click_button('Reopen'),
		() => assert.equal(cur_frm.doc.status, 'Open',
			'reopened'),
		() => capkpi.timeout(1),

		// make quotation
		() => capkpi.click_button('Make'),
		() => capkpi.click_link('Quotation', 1),
		() => capkpi.timeout(2),
		() => {
			assert.equal(capkpi.get_route()[1], 'Quotation',
				'made quotation');
			assert.equal(cur_frm.doc.customer, 'Test Customer 1',
				'customer set in quotation');
			assert.equal(cur_frm.doc.items[0].item_code, 'Test Product 1',
				'item set in quotation');
			assert.equal(cur_frm.doc.items[0].qty, 4,
				'qty set in quotation');
			assert.equal(cur_frm.doc.items[0].prevdoc_docname, capkpi.opportunity_name,
				'opportunity set in quotation');
		},
		() => done()
	]);
});
