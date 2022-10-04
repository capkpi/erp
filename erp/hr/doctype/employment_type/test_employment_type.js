QUnit.module('hr');

QUnit.test("Test: Employment type [HR]", function (assert) {
	assert.expect(1);
	let done = assert.async();

	capkpi.run_serially([
		// test employment type creation
		() => capkpi.set_route("List", "Employment Type", "List"),
		() => capkpi.new_doc("Employment Type"),
		() => capkpi.timeout(1),
		() => capkpi.quick_entry.dialog.$wrapper.find('.edit-full').click(),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("employee_type_name", "Test Employment type"),
		// save form
		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => assert.equal("Test Employment type", cur_frm.doc.employee_type_name,
			'name of employment type correctly saved'),
		() => done()
	]);
});
