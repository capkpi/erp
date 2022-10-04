/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Shopify Settings", function (assert) {
	let done = assert.async();

	// number of asserts
	assert.expect(1);

	capkpi.run_serially([
		// insert a new Shopify Settings
		() => capkpi.tests.make('Shopify Settings', [
			// values to be set
			{key: 'value'}
		]),
		() => {
			assert.equal(cur_frm.doc.key, 'value');
		},
		() => done()
	]);

});
