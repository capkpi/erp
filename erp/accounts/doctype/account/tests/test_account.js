QUnit.module('accounts');

QUnit.test("test account", function(assert) {
	assert.expect(4);
	let done = assert.async();
	capkpi.run_serially([
		() => capkpi.set_route('Tree', 'Account'),
		() => capkpi.timeout(3),
		() => capkpi.click_button('Expand All'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Debtors'),
		() => capkpi.click_button('Edit'),
		() => capkpi.timeout(1),
		() => {
			assert.ok(cur_frm.doc.root_type=='Asset');
			assert.ok(cur_frm.doc.report_type=='Balance Sheet');
			assert.ok(cur_frm.doc.account_type=='Receivable');
		},
		() => capkpi.click_button('Ledger'),
		() => capkpi.timeout(1),
		() => {
			// check if general ledger report shown
			assert.deepEqual(capkpi.get_route(), ['query-report', 'General Ledger']);
			window.history.back();
			return capkpi.timeout(1);
		},
		() => done()
	]);
});
