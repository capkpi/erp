// Testing Attendance Module in Education
QUnit.module('education');

QUnit.test('Test: Student Leave Application', function(assert){
	assert.expect(4);
	let done = assert.async();
	let student_code;
	let leave_code;
	capkpi.run_serially([
		() => capkpi.db.get_value('Student', {'student_email_id': 'test2@testmail.com'}, 'name'),
		(student) => {student_code = student.message.name;}, // fetching student code from db

		() => {
			return capkpi.tests.make('Student Leave Application', [
				{student: student_code},
				{from_date: '2017-08-02'},
				{to_date: '2017-08-04'},
				{mark_as_present: 0},
				{reason: "Sick Leave."}
			]);
		},
		() => capkpi.tests.click_button('Submit'), // Submitting the leave application
		() => capkpi.timeout(0.7),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.7),
		() => {
			assert.equal(cur_frm.doc.docstatus, 1, "Submitted leave application");
			leave_code = capkpi.get_route()[2];
		},
		() => capkpi.tests.click_button('Cancel'), // Cancelling the leave application
		() => capkpi.timeout(0.7),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(1),
		() => {assert.equal(cur_frm.doc.docstatus, 2, "Cancelled leave application");},
		() => capkpi.tests.click_button('Amend'), // Amending the leave application
		() => capkpi.timeout(1),
		() => {
			cur_frm.doc.mark_as_present = 1;
			cur_frm.save();
		},
		() => capkpi.timeout(0.7),
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.timeout(0.7),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.7),
		() => {assert.equal(cur_frm.doc.amended_from, leave_code, "Amended successfully");},

		() => capkpi.timeout(0.5),
		() => {
			return capkpi.tests.make('Student Leave Application', [
				{student: student_code},
				{from_date: '2017-08-07'},
				{to_date: '2017-08-09'},
				{mark_as_present: 0},
				{reason: "Sick Leave."}
			]);
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.timeout(0.7),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.7),
		() => {
			assert.equal(cur_frm.doc.docstatus, 1, "Submitted leave application");
			leave_code = capkpi.get_route()[2];
		},

		() => done()
	]);
});
