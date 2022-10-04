QUnit.test("test: Activity Type", function (assert) {
	// number of asserts
	assert.expect(1);
	let done = assert.async();

	capkpi.run_serially([
		// insert a new Activity Type
		() => capkpi.set_route("List", "Activity Type", "List"),
		() => capkpi.new_doc("Activity Type"),
		() => capkpi.timeout(1),
		() => capkpi.quick_entry.dialog.$wrapper.find('.edit-full').click(),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("activity_type", "Test Activity"),
		() => capkpi.click_button('Save'),
		() => capkpi.timeout(1),
		() => {
			assert.equal(cur_frm.doc.name,"Test Activity");
		},
		() => done()
	]);
});
