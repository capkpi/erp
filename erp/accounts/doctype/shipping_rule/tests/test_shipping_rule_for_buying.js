QUnit.module('Shipping Rule');

QUnit.test("test Shipping Rule", function(assert) {
	assert.expect(1);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make("Shipping Rule", [
				{label: "Two Day Shipping"},
				{shipping_rule_type: "Buying"},
				{fixed_shipping_amount: 0},
				{conditions:[
					[
						{from_value:1},
						{to_value:200},
						{shipping_amount:100}
					],
					[
						{from_value:201},
						{to_value:3000},
						{shipping_amount:200}
					],
				]},
				{countries:[
					[
						{country:'India'}
					]
				]},
				{account:'Accounts Payable - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))},
				{cost_center:'Main - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
			]);
		},
		() => {assert.ok(cur_frm.doc.name=='Two Day Shipping');},
		() => done()
	]);
});
