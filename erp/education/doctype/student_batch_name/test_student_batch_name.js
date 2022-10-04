// Testing Setup Module in Education
QUnit.module('education');

QUnit.test('Test: Student Batch Name', function(assert){
	assert.expect(1);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Student Batch Name', [
				{batch_name: 'A'}
			]);
		},
		() => cur_frm.save(),
		() => {
			assert.ok(cur_frm.doc.batch_name=='A');
		},
		() => done()
	]);
});
