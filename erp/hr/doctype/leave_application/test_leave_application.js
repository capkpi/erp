QUnit.module('hr');

QUnit.test("Test: Leave application [HR]", function (assert) {
	assert.expect(4);
	let done = assert.async();
	let today_date = capkpi.datetime.nowdate();
	let leave_date = capkpi.datetime.add_days(today_date, 1);	// leave for tomorrow

	capkpi.run_serially([
		// test creating leave application
		() => capkpi.db.get_value('Employee', {'employee_name':'Test Employee 1'}, 'name'),
		(employee) => {
			return capkpi.tests.make('Leave Application', [
				{leave_type: "Test Leave type"},
				{from_date: leave_date},	// for today
				{to_date: leave_date},
				{half_day: 1},
				{employee: employee.message.name},
				{follow_via_email: 0}
			]);
		},

		() => capkpi.timeout(1),
		() => capkpi.click_button('Actions'),
		() => capkpi.click_link('Approve'), // approve the application [as administrator]
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(1),
		() => assert.ok(cur_frm.doc.docstatus,
			"leave application submitted after approval"),

		// check auto filled posting date [today]

		() => assert.equal(today_date, cur_frm.doc.posting_date,
			"posting date correctly set"),
		() => capkpi.set_route("List", "Leave Application", "List"),
		() => capkpi.timeout(1),
		// // check approved application in list
		() => assert.deepEqual(["Test Employee 1", 1], [cur_list.data[0].employee_name, cur_list.data[0].docstatus]),
		// 	"leave for correct employee is submitted"),
		() => done()
	]);
});
