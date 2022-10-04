QUnit.module('accounts');

QUnit.test("test account with number", function(assert) {
	assert.expect(7);
	let done = assert.async();
	capkpi.run_serially([
		() => capkpi.set_route('Tree', 'Account'),
		() => capkpi.click_link('Income'),
		() => capkpi.click_button('Add Child'),
		() => capkpi.timeout(.5),
		() => {
			cur_dialog.fields_dict.account_name.$input.val("Test Income");
			cur_dialog.fields_dict.account_number.$input.val("4010");
		},
		() => capkpi.click_button('Create New'),
		() => capkpi.timeout(1),
		() => {
			assert.ok($('a:contains("4010 - Test Income"):visible').length!=0, "Account created with number");
		},
		() => capkpi.click_link('4010 - Test Income'),
		() => capkpi.click_button('Edit'),
		() => capkpi.timeout(.5),
		() => capkpi.click_button('Update Account Number'),
		() => capkpi.timeout(.5),
		() => {
			cur_dialog.fields_dict.account_number.$input.val("4020");
		},
		() => capkpi.timeout(1),
		() => cur_dialog.primary_action(),
		() => capkpi.timeout(1),
		() => cur_frm.refresh_fields(),
		() => capkpi.timeout(.5),
		() => {
			var abbr = capkpi.get_abbr(capkpi.defaults.get_default("Company"));
			var new_account = "4020 - Test Income - " + abbr;
			assert.ok(cur_frm.doc.name==new_account, "Account renamed");
			assert.ok(cur_frm.doc.account_name=="Test Income", "account name remained same");
			assert.ok(cur_frm.doc.account_number=="4020", "Account number updated to 4020");
		},
		() => capkpi.timeout(1),
		() => capkpi.click_button('Menu'),
		() => capkpi.click_link('Rename'),
		() => capkpi.timeout(.5),
		() => {
			cur_dialog.fields_dict.new_name.$input.val("4030 - Test Income");
		},
		() => capkpi.timeout(.5),
		() => capkpi.click_button("Rename"),
		() => capkpi.timeout(2),
		() => {
			assert.ok(cur_frm.doc.account_name=="Test Income", "account name remained same");
			assert.ok(cur_frm.doc.account_number=="4030", "Account number updated to 4030");
		},
		() => capkpi.timeout(.5),
		() => capkpi.click_button('Chart of Accounts'),
		() => capkpi.timeout(.5),
		() => capkpi.click_button('Menu'),
		() => capkpi.click_link('Refresh'),
		() => capkpi.click_button('Expand All'),
		() => capkpi.click_link('4030 - Test Income'),
		() => capkpi.click_button('Delete'),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(.5),
		() => {
			assert.ok($('a:contains("4030 - Test Account"):visible').length==0, "Account deleted");
		},
		() => done()
	]);
});
