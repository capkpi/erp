QUnit.module('Accounts');

QUnit.test("test payment entry", function(assert) {
	assert.expect(1);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Payment Entry', [
				{payment_type:'Receive'},
				{mode_of_payment:'Cash'},
				{party_type:'Customer'},
				{party:'Test Customer 3'},
				{paid_amount:675},
				{reference_no:123},
				{reference_date: capkpi.datetime.add_days(capkpi.datetime.nowdate(), 0)},
			]);
		},
		() => cur_frm.save(),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.total_allocated_amount==675, "Allocated AmountCorrect");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
