QUnit.module('Stock');

QUnit.test("test manufacture from bom", function(assert) {
	assert.expect(2);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make("Stock Entry", [
				{ purpose: "Manufacture" },
				{ from_bom: 1 },
				{ bom_no: "BOM-_Test Item - Non Whole UOM-001" },
				{ fg_completed_qty: 2 }
			]);
		},
		() => cur_frm.save(),
		() => capkpi.click_button("Update Rate and Availability"),
		() => {
			assert.ok(cur_frm.doc.items[1] === 0.75, " Finished Item Qty correct");
			assert.ok(cur_frm.doc.items[2] === 0.25, " Process Loss Item Qty correct");
		},
		() => capkpi.tests.click_button('Submit'),
		() => capkpi.tests.click_button('Yes'),
		() => capkpi.timeout(0.3),
		() => done()
	]);
});

