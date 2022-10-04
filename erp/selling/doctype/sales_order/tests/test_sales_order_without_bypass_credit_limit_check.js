QUnit.module('Sales Order');

QUnit.test("test_sales_order_without_bypass_credit_limit_check", function(assert) {
//#PR : 10861, Author : ashish-greycube & jigneshpshah,  Email:mr.ashish.shah@gmail.com
	assert.expect(2);
	let done = assert.async();
	capkpi.run_serially([
		() => capkpi.new_doc('Customer'),
		() => capkpi.timeout(1),
		() => capkpi.quick_entry.dialog.$wrapper.find('.edit-full').click(),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("customer_name", "Test Customer 11"),
		() => cur_frm.add_child('credit_limits', {
			'credit_limit': 1000,
			'company': '_Test Company',
			'bypass_credit_limit_check': 1}),
		// save form
		() => cur_frm.save(),
		() => capkpi.timeout(1),

		() => capkpi.new_doc('Item'),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Edit in full page'),
		() => cur_frm.set_value("item_code", "Test Product 11"),
		() => cur_frm.set_value("item_group", "Products"),
		() => cur_frm.set_value("standard_rate", 100),
		// save form
		() => cur_frm.save(),
		() => capkpi.timeout(1),

		() => {
			return capkpi.tests.make('Sales Order', [
				{customer: 'Test Customer 11'},
				{items: [
					[
						{'delivery_date': capkpi.datetime.add_days(capkpi.defaults.get_default("year_end_date"), 1)},
						{'qty': 5},
						{'item_code': 'Test Product 11'},
					]
				]}

			]);
		},
		() => cur_frm.save(),
		() => capkpi.tests.click_button('Submit'),
		() => assert.equal("Confirm", cur_dialog.title,'confirmation for submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(3),
		() => {

			if (cur_dialog.body.innerText.match(/^Credit limit has been crossed for customer.*$/))
				{
    				/*Match found */
    				assert.ok(true, "Credit Limit crossed message received");
				}


		},
		() => cur_dialog.cancel(),
		() => done()
	]);
});
