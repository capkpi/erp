QUnit.module("sales");

QUnit.test("test: lead", function (assert) {
	assert.expect(5);
	let done = assert.async();
	let lead_name = capkpi.utils.get_random(10);
	capkpi.run_serially([
		// test lead creation
		() => capkpi.set_route("List", "Lead"),
		() => capkpi.new_doc("Lead"),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("organization_lead", "1"),
		() => cur_frm.set_value("company_name", lead_name),
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

		() => capkpi.click_button('New Contact'),
		() => capkpi.timeout(1),
		() => capkpi.set_control('first_name', 'John'),
		() => capkpi.set_control('last_name', 'Doe'),
		() => cur_frm.save(),
		() => capkpi.timeout(3),
		() => capkpi.set_route('Form', 'Lead', cur_frm.doc.links[0].link_name),
		() => capkpi.timeout(1),
		() => capkpi.click_link('Address & Contact'),
		() => assert.ok($('.address-box').text().includes('John'),
			'contact is seen in contact box'),

		// make customer
		() => capkpi.click_button('Make'),
		() => capkpi.click_link('Customer'),
		() => capkpi.timeout(2),
		() => assert.equal(cur_frm.doc.lead_name, capkpi.lead_name,
			'lead name correctly mapped'),

		() => done()
	]);
});
