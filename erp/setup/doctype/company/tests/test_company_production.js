QUnit.test("Test: Company", function (assert) {
	assert.expect(0);

	let done = assert.async();

	capkpi.run_serially([
		// Added company for Work Order testing
		() => capkpi.set_route("List", "Company"),
		() => capkpi.new_doc("Company"),
		() => capkpi.timeout(1),
		() => cur_frm.set_value("company_name", "For Testing"),
		() => cur_frm.set_value("abbr", "RB"),
		() => cur_frm.set_value("default_currency", "INR"),
		() => cur_frm.save(),
		() => capkpi.timeout(1),

		() => done()
	]);
});
