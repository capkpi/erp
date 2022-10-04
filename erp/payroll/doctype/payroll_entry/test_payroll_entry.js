QUnit.module('HR');

QUnit.test("test: Payroll Entry", function (assert) {
	assert.expect(5);
	let done = assert.async();
	let employees, docname;

	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Payroll Entry', [
				{company: 'For Testing'},
				{posting_date: capkpi.datetime.add_days(capkpi.datetime.nowdate(), 0)},
				{payroll_frequency: 'Monthly'},
				{cost_center: 'Main - '+capkpi.get_abbr(capkpi.defaults.get_default("Company"))}
			]);
		},

		() => capkpi.timeout(1),
		() => {
			assert.equal(cur_frm.doc.company, 'For Testing');
			assert.equal(cur_frm.doc.posting_date, capkpi.datetime.add_days(capkpi.datetime.nowdate(), 0));
			assert.equal(cur_frm.doc.cost_center, 'Main - FT');
		},
		() => capkpi.click_button('Get Employee Details'),
		() => {
			employees = cur_frm.doc.employees.length;
			docname = cur_frm.doc.name;
		},

		() => capkpi.click_button('Submit'),
		() => capkpi.timeout(1),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(5),

		() => capkpi.click_button('View Salary Slip'),
		() => capkpi.timeout(2),
		() => assert.equal(cur_list.data.length, employees),

		() => capkpi.set_route('Form', 'Payroll Entry', docname),
		() => capkpi.timeout(2),
		() => capkpi.click_button('Submit Salary Slip'),
		() => capkpi.click_button('Yes'),
		() => capkpi.timeout(5),

		() => capkpi.click_button('Close'),
		() => capkpi.timeout(1),

		() => capkpi.click_button('View Salary Slip'),
		() => capkpi.timeout(2),
		() => {
			let count = 0;
			for(var i = 0; i < employees; i++) {
				if(cur_list.data[i].docstatus == 1){
					count++;
				}
			}
			assert.equal(count, employees, "Salary Slip submitted for all employees");
		},

		() => done()
	]);
});
