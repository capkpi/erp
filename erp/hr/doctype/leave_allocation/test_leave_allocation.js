QUnit.module('hr');

QUnit.test("Test: Leave allocation [HR]", function (assert) {
	assert.expect(3);
	let done = assert.async();
	let today_date = capkpi.datetime.nowdate();

	capkpi.run_serially([
		// test creating leave alloction
		() => capkpi.set_route("List", "Leave Allocation", "List"),
		() => capkpi.new_doc("Leave Allocation"),
		() => capkpi.timeout(1),
		() => {
			capkpi.db.get_value('Employee', {'employee_name':'Test Employee 1'}, 'name', function(r) {
				cur_frm.set_value("employee", r.name)
			});
		},
		() => capkpi.timeout(1),
		() => cur_frm.set_value("leave_type", "Test Leave type"),
		() => cur_frm.set_value("to_date", capkpi.datetime.add_months(today_date, 2)),	// for two months
		() => cur_frm.set_value("description", "This is just for testing"),
		() => cur_frm.set_value("new_leaves_allocated", 2),
		() => capkpi.click_check('Add unused leaves from previous allocations'),
		// save form
		() => cur_frm.save(),
		() => capkpi.timeout(1),
		() => cur_frm.savesubmit(),
		() => capkpi.timeout(1),
		() => assert.equal("Confirm", cur_dialog.title,
			'confirmation for leave alloction shown'),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(1),
		// check auto filled from date
		() => assert.equal(today_date, cur_frm.doc.from_date,
			"from date correctly set"),
		// check for total leaves
		() => assert.equal(cur_frm.doc.unused_leaves + 2, cur_frm.doc.total_leaves_allocated,
			"total leave calculation is correctly set"),
		() => done()
	]);
});
