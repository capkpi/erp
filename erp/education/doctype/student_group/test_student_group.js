// Testing Student Module in Education
QUnit.module('education');

QUnit.test('Test: Student Group', function(assert){
	assert.expect(2);
	let done = assert.async();
	let group_based_on = ["test-batch-wise-group", "test-course-wise-group"];
	let tasks = [];

	capkpi.run_serially([
		// Creating a Batch and Course based group
		() => {
			return capkpi.tests.make('Student Group', [
				{academic_year: '2016-17'},
				{academic_term: '2016-17 (Semester 1)'},
				{program: "Standard Test"},
				{group_based_on: 'Batch'},
				{student_group_name: group_based_on[0]},
				{max_strength: 10},
				{batch: 'A'}
			]);
		},
		() => {
			return capkpi.tests.make('Student Group', [
				{academic_year: '2016-17'},
				{academic_term: '2016-17 (Semester 1)'},
				{program: "Standard Test"},
				{group_based_on: 'Course'},
				{student_group_name: group_based_on[1]},
				{max_strength: 10},
				{batch: 'A'},
				{course: 'Test_Sub'},
			]);
		},

		// Populating the created group with Students
		() => {
			tasks = [];
			group_based_on.forEach(index => {
				tasks.push(
					() => capkpi.timeout(0.5),
					() => capkpi.set_route("Form", ('Student Group/' + index)),
					() => capkpi.timeout(0.5),
					() => capkpi.tests.click_button('Get Students'),
					() => capkpi.timeout(1),
					() => {
						assert.equal(cur_frm.doc.students.length, 5, 'Successfully fetched list of students');
					},
				);
			});
			return capkpi.run_serially(tasks);
		},

		() => done()
	]);
});
