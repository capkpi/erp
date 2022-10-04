QUnit.module('Payment Entry');

QUnit.test("test payment entry", function(assert) {
	assert.expect(6);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Sales Invoice', [
				{customer: 'Test Customer 1'},
				{items: [
					[
						{'item_code': 'Test Product 1'},
						{'qty': 1},
						{'rate': 101},
					]
				]}
			]);
		},
		() => cur_frm.save(),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(1),
		() => capkpi.tests.click_button('Close'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Make'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Payment'),
		() => capkpi.timeout(2),
		() => {
			assert.equal(capkpi.get_route()[1], 'Payment Entry',
				'made payment entry');
			assert.equal(cur_frm.doc.party, 'Test Customer 1',
				'customer set in payment entry');
			assert.equal(cur_frm.doc.paid_amount, 101,
				'paid amount set in payment entry');
			assert.equal(cur_frm.doc.references[0].allocated_amount, 101,
				'amount allocated against sales invoice');
		},
		() => capkpi.timeout(1),
		() => cur_frm.set_value('paid_amount', 100),
		() => capkpi.timeout(1),
		() => {
			capkpi.model.set_value("Payment Entry Reference", cur_frm.doc.references[0].name,
				"allocated_amount", 101);
		},
		() => capkpi.timeout(1),
		() => capkpi.click_button('Write Off Difference Amount'),
		() => capkpi.timeout(1),
		() => {
			assert.equal(cur_frm.doc.difference_amount, 0, 'difference amount is zero');
			assert.equal(cur_frm.doc.deductions[0].amount, 1, 'Write off amount = 1');
		},
		() => done()
	]);
});
