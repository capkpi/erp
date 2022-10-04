/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Fertilizer", function (assert) {
	let done = assert.async();

	// number of asserts
	assert.expect(1);

	capkpi.run_serially([
		// insert a new Item
		() => capkpi.tests.make('Item', [
			// values to be set
			{item_code: 'Urea'},
			{item_name: 'Urea'},
			{item_group: 'Fertilizer'}
		]),
		// insert a new Fertilizer
		() => capkpi.tests.make('Fertilizer', [
			// values to be set
			{fertilizer_name: 'Urea'},
			{item: 'Urea'}
		]),
		() => {
			assert.equal(cur_frm.doc.name, 'Urea');
		},
		() => done()
	]);

});
