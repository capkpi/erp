// Education Assessment module
QUnit.module('education');

QUnit.test('Test: Assessment Criteria Group', function(assert){
	assert.expect(0);
	let done = assert.async();
	capkpi.run_serially([
		() => {
			return capkpi.tests.make('Assessment Criteria Group', [
				{assessment_criteria_group: 'Reservation'}
			]);
		},
		() => done()
	]);
});
