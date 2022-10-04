/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Task Tree", function (assert) {
	let done = assert.async();

	// number of asserts
	assert.expect(4);

	capkpi.run_serially([
		// insert a new Task
		() => capkpi.set_route('Tree', 'Task'),
		() => capkpi.timeout(0.5),

		// Checking adding child without selecting any Node
		() => capkpi.tests.click_button('New'),
		() => capkpi.timeout(0.5),
		() => {assert.equal($(`.msgprint`).text(), "Select a group node first.", "Error message success");},
		() => capkpi.tests.click_button('Close'),
		() => capkpi.timeout(0.5),

		// Creating child nodes
		() => capkpi.tests.click_link('All Tasks'),
		() => capkpi.map_group.make('Test-1'),
		() => capkpi.map_group.make('Test-3', 1),
		() => capkpi.timeout(1),
		() => capkpi.tests.click_link('Test-3'),
		() => capkpi.map_group.make('Test-4', 0),

		// Checking Edit button
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_link('Test-1'),
		() => capkpi.tests.click_button('Edit'),
		() => capkpi.timeout(1),
		() => capkpi.db.get_value('Task', {'subject': 'Test-1'}, 'name'),
		(task) => {assert.deepEqual(capkpi.get_route(), ["Form", "Task", task.message.name], "Edit route checks");},

		// Deleting child Node
		() => capkpi.set_route('Tree', 'Task'),
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_link('Test-1'),
		() => capkpi.tests.click_button('Delete'),
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_button('Yes'),

		// Deleting Group Node that has child nodes in it
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_link('Test-3'),
		() => capkpi.tests.click_button('Delete'),
		() => capkpi.timeout(0.5),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(1),
		() => {assert.equal(cur_dialog.title, 'Message', 'Error thrown correctly');},
		() => capkpi.tests.click_button('Close'),

		// Add multiple child tasks
		() => capkpi.tests.click_link('Test-3'),
		() => capkpi.timeout(0.5),
		() => capkpi.click_button('Add Multiple'),
		() => capkpi.timeout(1),
		() => cur_dialog.set_value('tasks', 'Test-6\nTest-7'),
		() => capkpi.timeout(0.5),
		() => capkpi.click_button('Submit'),
		() => capkpi.timeout(2),
		() => capkpi.click_button('Expand All'),
		() => capkpi.timeout(1),
		() => {
			let count = $(`a:contains("Test-6"):visible`).length + $(`a:contains("Test-7"):visible`).length;
			assert.equal(count, 2, "Multiple Tasks added successfully");
		},

		() => done()
	]);
});

capkpi.map_group = {
	make:function(subject, is_group = 0){
		return capkpi.run_serially([
			() => capkpi.click_button('Add Child'),
			() => capkpi.timeout(1),
			() => cur_dialog.set_value('is_group', is_group),
			() => cur_dialog.set_value('subject', subject),
			() => capkpi.click_button('Create New'),
			() => capkpi.timeout(1.5)
		]);
	}
};
