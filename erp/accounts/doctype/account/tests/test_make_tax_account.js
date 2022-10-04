QUnit.module('accounts');
QUnit.test("test account", assert => {
	assert.expect(3);
	let done = assert.async();
	capkpi.run_serially([
		() => capkpi.set_route('Tree', 'Account'),
		() => capkpi.click_button('Expand All'),
		() => capkpi.click_link('Duties and Taxes - '+ capkpi.get_abbr(capkpi.defaults.get_default("Company"))),
		() => {
			if($('a:contains("CGST"):visible').length == 0){
				return capkpi.map_tax.make('CGST', 9);
			}
		},
		() => {
			if($('a:contains("SGST"):visible').length == 0){
				return capkpi.map_tax.make('SGST', 9);
			}
		},
		() => {
			if($('a:contains("IGST"):visible').length == 0){
				return capkpi.map_tax.make('IGST', 18);
			}
		},
		() => {
			assert.ok($('a:contains("CGST"):visible').length!=0, "CGST Checked");
			assert.ok($('a:contains("SGST"):visible').length!=0, "SGST Checked");
			assert.ok($('a:contains("IGST"):visible').length!=0, "IGST Checked");
		},
		() => done()
	]);
});


capkpi.map_tax = {
	make:function(text,rate){
		return capkpi.run_serially([
			() => capkpi.click_button('Add Child'),
			() => capkpi.timeout(0.2),
			() => cur_dialog.set_value('account_name',text),
			() => cur_dialog.set_value('account_type','Tax'),
			() => cur_dialog.set_value('tax_rate',rate),
			() => cur_dialog.set_value('account_currency','INR'),
			() => capkpi.click_button('Create New'),
		]);
	}
};
