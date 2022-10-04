QUnit.module("sales");

QUnit.test("test: lead", function (assert) {
	assert.expect(4);
	let done = assert.async();
	let lead_name = capkpi.utils.get_random(10);
	capkpi.run_serially([
		// test lead creation
		() => capkpi.set_route("List", "Lead"),
		() => capkpi.new_doc("Lead"),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("lead_name", lead_name),
		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => {
			assert.ok(cur_frm.doc.lead_name.includes(lead_name),
				'name correctly set');
			capkpi.lead_name = cur_frm.doc.name;
		},
		// create address and contact
		() => capkpi.click_link('Address & Contact'),
		() => capkpi.click_button('New Address'),
		() => capkpi.timeout(1),
		() => capkpi.set_control('address_line1', 'Gateway'),
		() => capkpi.set_control('city', 'Mumbai'),
		() => cur_frm.save(),
		() => capkpi.timeout(3),
		() => assert.equal(capkpi.get_route()[1], 'Lead',
			'back to lead form'),
		() => capkpi.click_link('Address & Contact'),
		() => assert.ok($('.address-box').text().includes('Mumbai'),
			'city is seen in address box'),

		// make opportunity
		() => capkpi.click_button('Make'),
		() => capkpi.click_link('Opportunity'),
		() => capkpi.timeout(2),
		() => assert.equal(cur_frm.doc.lead, capkpi.lead_name,
			'lead name correctly mapped'),

		() => done()
	]);
});
