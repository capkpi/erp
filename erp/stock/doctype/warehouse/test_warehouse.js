QUnit.test("test: warehouse", function (assert) {
	assert.expect(0);
	let done = assert.async();

	capkpi.run_serially([
		// test warehouse creation
		() => capkpi.set_route("List", "Warehouse"),

		// Create a Laptop Scrap Warehouse
		() => capkpi.tests.make(
			"Warehouse", [
				{warehouse_name: "Laptop Scrap Warehouse"},
				{company: "For Testing"}
			]
		),

		() => done()
	]);
});
