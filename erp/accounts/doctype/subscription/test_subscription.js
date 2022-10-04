/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Subscription", function (assert) {
	assert.expect(4);
	let done = assert.async();
	capkpi.run_serially([
		// insert a new Subscription
		() => {
			return capkpi.tests.make("Subscription", [
				{reference_doctype: 'Sales Invoice'},
				{reference_document: 'SINV-00004'},
				{start_date: capkpi.datetime.month_start()},
				{end_date: capkpi.datetime.month_end()},
				{frequency: 'Weekly'}
			]);
		},
		() => cur_frm.savesubmit(),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(2),
		() => {
			assert.ok(cur_frm.doc.frequency.includes("Weekly"), "Set frequency Weekly");
			assert.ok(cur_frm.doc.reference_doctype.includes("Sales Invoice"), "Set base doctype Sales Invoice");
			assert.equal(cur_frm.doc.docstatus, 1, "Submitted subscription");
			assert.equal(cur_frm.doc.next_schedule_date,
				capkpi.datetime.add_days(capkpi.datetime.get_today(), 7),  "Set schedule date");
		},
		() => done()
	]);
});
