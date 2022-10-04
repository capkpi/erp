/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Workstation", function (assert) {
	let done = assert.async();

	// number of asserts
	assert.expect(1);

	capkpi.run_serially('Workstation', [
		// insert a new Workstation
		() => capkpi.tests.make([
			// values to be set
			{key: 'value'}
		]),
		() => {
			assert.equal(cur_frm.doc.key, 'value');
		},
		() => done()
	]);

});