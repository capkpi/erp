// Education Assessment module
QUnit.module('education');

QUnit.test('Test: Assessment Result', function(assert){
	assert.expect(25);
	let done = assert.async();
	let student_list = [];
	let assessment_name;
	let tasks = []

	capkpi.run_serially([
		// Saving Assessment Plan name
		() => capkpi.db.get_value('Assessment Plan', {'assessment_name': 'Test-Mid-Term'}, 'name'),
		(assessment_plan) => {assessment_name = assessment_plan.message.name;},
		// Fetching list of Student for which Result is supposed to be set
		() => capkpi.set_route('Form', 'Assessment Plan', assessment_name),
		() => capkpi.timeout(1),
		() => capkpi.tests.click_button('Assessment Result'),
		() => capkpi.timeout(1),
		() => cur_frm.refresh(),
		() => capkpi.timeout(1),
		() => {
			$("tbody tr").each( function(i, input){
				student_list.push($(input).data().student);
			});
		},

		// Looping through each student in the list and setting up their score
		() => {
			student_list.forEach(index => {
				tasks.push(
					() => capkpi.set_route('List', 'Assessment Result', 'List'),
					() => capkpi.timeout(0.5),
					() => capkpi.tests.click_button('New'),
					() => capkpi.timeout(0.5),
					() => cur_frm.set_value('student', index),
					() => cur_frm.set_value('assessment_plan', assessment_name),
					() => capkpi.timeout(0.2),
					() => cur_frm.doc.details[0].score = (39 + (15 * student_list.indexOf(index))),
					() => cur_frm.save(),
					() => capkpi.timeout(0.5),

					() => capkpi.db.get_value('Assessment Plan', {'name': 'ASP00001'}, ['grading_scale', 'maximum_assessment_score']),
					(assessment_plan) => {
						assert.equal(cur_frm.doc.grading_scale, assessment_plan.message.grading_scale, 'Grading scale correctly fetched');
						assert.equal(cur_frm.doc.maximum_score, assessment_plan.message.maximum_assessment_score, 'Maximum score correctly fetched');

						capkpi.call({
							method: "erp.education.api.get_grade",
							args: {
								"grading_scale": assessment_plan.message.grading_scale,
								"percentage": cur_frm.doc.total_score
							},
							callback: function(r){
								assert.equal(cur_frm.doc.grade, r.message, "Grade correctly calculated");
							}
						});
					},

					() => capkpi.tests.click_button('Submit'),
					() => capkpi.timeout(0.5),
					() => capkpi.tests.click_button('Yes'),
					() => capkpi.timeout(0.5),
					() => {assert.equal();},
					() => {assert.equal(cur_frm.doc.docstatus, 1, "Submitted successfully");},
				);
			});
			return capkpi.run_serially(tasks);
		},

		() => done()
	]);
});
