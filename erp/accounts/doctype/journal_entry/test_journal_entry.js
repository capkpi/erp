QUnit.module('Journal Entry');

QUnit.test("test journal entry", function(assert) {
	assert.expect(2);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Journal Entry', [
				{posting_date:capkpi.datetime.add_days(capkpi.datetime.nowdate(), 0)},
				{accounts: [
					[
						{'account':'Debtors - '+capkpi.get_abbr(capkpi.defaults.get_default('Company'))},
						{'party_type':'Customer'},
						{'party':'Test Customer 1'},
						{'credit_in_account_currency':1000},
						{'is_advance':'Yes'},
					],
					[
						{'account':'HDFC - '+capkpi.get_abbr(capkpi.defaults.get_default('Company'))},
						{'debit_in_account_currency':1000},
					]
				]},
				{cheque_no:1234},
				{cheque_date: capkpi.datetime.add_days(capkpi.datetime.nowdate(), -1)},
				{user_remark: 'Test'},
			]);
		},
		() => cur_frm.save(),
		() => {
			// get_item_details
			assert.ok(cur_frm.doc.total_debit==1000, "total debit correct");
			assert.ok(cur_frm.doc.total_credit==1000, "total credit correct");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});
