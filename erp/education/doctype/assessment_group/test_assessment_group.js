// Education Assessment module
QUnit.module('education');

QUnit.test('Test: Assessment Group', function(assert){
	assert.expect(4);
	let done = assert.async();

	capkpi.run_serially([
		() => capkpi.set_route('Tree', 'Assessment Group'),

		// Checking adding child without selecting any Node
		() => capkpi.tests.click_button('New'),
		() => capkpi.timeout(0.2),
		() => {assert.equal($(`.msgprint`).text(), "Select a group node first.", "Error message success");},
		() => capkpi.tests.click_button('Close'),
		() => capkpi.timeout(0.2),

		// Creating child nodes
		() => capkpi.tests.click_link('All Assessment Groups'),
		() => capkpi.map_group.make('Assessment-group-1'),
		() => capkpi.map_group.make('Assessment-group-4', "All Assessment Groups", 1),
		() => capkpi.tests.click_link('Assessment-group-4'),
		() => capkpi.map_group.make('Assessment-group-5', "Assessment-group-3", 0),

		// Checking Edit button
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_link('Assessment-group-1'),
		() => capkpi.tests.click_button('Edit'),
		() => capkpi.timeout(0.5),
		() => {assert.deepEqual(capkpi.get_route(), ["Form", "Assessment Group", "Assessment-group-1"], "Edit route checks");},

		// Deleting child Node
		() => capkpi.set_route('Tree', 'Assessment Group'),
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_link('Assessment-group-1'),
		() => capkpi.tests.click_button('Delete'),
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_button('Yes'),

		// Checking Collapse and Expand button
		() => capkpi.timeout(2),
		() => capkpi.tests.click_link('Assessment-group-4'),
		() => capkpi.click_button('Collapse'),
		() => capkpi.tests.click_link('All Assessment Groups'),
		() => capkpi.click_button('Collapse'),
		() => {assert.ok($('.opened').size() == 0, 'Collapsed');},
		() => capkpi.click_button('Expand'),
		() => {assert.ok($('.opened').size() > 0, 'Expanded');},

		() => done()
	]);
});

capkpi.map_group = {
	make:function(assessment_group_name, parent_assessment_group = 'All Assessment Groups', is_group = 0){
		return capkpi.run_serially([
			() => capkpi.click_button('Add Child'),
			() => capkpi.timeout(0.2),
			() => cur_dialog.set_value('is_group', is_group),
			() => cur_dialog.set_value('assessment_group_name', assessment_group_name),
			() => cur_dialog.set_value('parent_assessment_group', parent_assessment_group),
			() => capkpi.click_button('Create New'),
		]);
	}
};
