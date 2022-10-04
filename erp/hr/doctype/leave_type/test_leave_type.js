QUnit.module('hr');

QUnit.test("Test: Leave type [HR]", function (assert) {
	assert.expect(1);
	let done = assert.async();

	capkpi.run_serially([
		// test leave type creation
		() => capkpi.set_route("List", "Leave Type", "List"),
		() => capkpi.new_doc("Leave Type"),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("leave_type_name", "Test Leave type"),
		() => cur_frm.set_value("max_continuous_days_allowed", "5"),
		() => capkpi.click_check('Is Carry Forward'),
		// save form
		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => assert.equal("Test Leave type", cur_frm.doc.leave_type_name,
			'leave type correctly saved'),
		() => done()
	]);
});
