QUnit.module('Admission');

QUnit.test('Make Students', function(assert){
	assert.expect(0);
	let done = assert.async();
	let tasks = [];
	let loop = [1,2,3,4];
	let fname;

	capkpi.run_serially([
		// Making School House to be used in this test and later
		() => capkpi.set_route('Form', 'School House/New School House'),
		() => capkpi.timeout(0.5),
		() => cur_frm.doc.house_name = 'Test_house',
		() => cur_frm.save(),

		// Making Student Applicant entries
		() => {
			loop.forEach(index => {
				tasks.push(() => {
					fname = "Fname" + index;

					return capkpi.tests.make('Student Applicant', [
						{first_name: fname},
						{middle_name: "Mname"},
						{last_name: "Lname"},
						{program: "Standard Test"},
						{student_admission: "2016-17 Admissions"},
						{date_of_birth: '1995-08-20'},
						{student_email_id: ('test' + (index+3) + '@testmail.com')},
						{gender: 'Male'},
						{student_mobile_number: (9898980000 + index)},
						{blood_group: 'O+'},
						{address_line_1: 'Test appt, Test Society,'},
						{address_line_2: 'Test district, Test city.'},
						{city: 'Test'},
						{state: 'Test'},
						{pincode: '395007'}
					]);
				});
			});
			return capkpi.run_serially(tasks);
		},

		// Using Program Enrollment Tool to enroll all dummy student at once
		() => capkpi.set_route('Form', 'Program Enrollment Tool'),
		() => {
			cur_frm.set_value("get_students_from", "Student Applicants");
			cur_frm.set_value("academic_year", "2016-17");
			cur_frm.set_value("program", "Standard Test");
		},
		() => capkpi.tests.click_button("Get Students"),
		() => capkpi.timeout(1),
		() => capkpi.tests.click_button("Enroll Students"),
		() => capkpi.timeout(1.5),
		() => capkpi.tests.click_button("Close"),

		// Submitting required data for each enrolled Student
		() => {
			tasks = [];
			loop.forEach(index => {
				tasks.push(
					() => {fname = "Fname" + index + " Mname Lname";},
					() => capkpi.set_route('List', 'Program Enrollment/List'),
					() => capkpi.timeout(0.6),
					() => capkpi.tests.click_link(fname),
					() => capkpi.timeout(0.4),
					() => {
						cur_frm.set_value('program', 'Standard Test');
						cur_frm.set_value('student_category', 'Reservation');
						cur_frm.set_value('student_batch_name', 'A');
						cur_frm.set_value('academic_year', '2016-17');
						cur_frm.set_value('academic_term', '2016-17 (Semester 1)');
						cur_frm.set_value('school_house', 'Test_house');
					},
					() => cur_frm.save(),
					() => capkpi.timeout(0.5),
					() => capkpi.tests.click_button('Submit'),
					() => capkpi.tests.click_button('Yes'),
					() => capkpi.timeout(0.5)
				);
			});
			return capkpi.run_serially(tasks);
		},
		() => done()
	]);
});
