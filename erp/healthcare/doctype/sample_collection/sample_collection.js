// Copyright (c) 2016, ESS and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Sample Collection', {
	refresh: function(frm) {
		if (capkpi.defaults.get_default('create_sample_collection_for_lab_test')) {
			frm.add_custom_button(__('View Lab Tests'), function() {
				capkpi.route_options = {'sample': frm.doc.name};
				capkpi.set_route('List', 'Lab Test');
			});
		}
	}
});

capkpi.ui.form.on('Sample Collection', 'patient', function(frm) {
	if(frm.doc.patient){
		capkpi.call({
			'method': 'erp.healthcare.doctype.patient.patient.get_patient_detail',
			args: {
				patient: frm.doc.patient
			},
			callback: function (data) {
				var age = null;
				if (data.message.dob){
					age = calculate_age(data.message.dob);
				}
				capkpi.model.set_value(frm.doctype,frm.docname, 'patient_age', age);
				capkpi.model.set_value(frm.doctype,frm.docname, 'patient_sex', data.message.sex);
			}
		});
	}
});

var calculate_age = function(birth) {
	var	ageMS = Date.parse(Date()) - Date.parse(birth);
	var	age = new Date();
	age.setTime(ageMS);
	var	years =  age.getFullYear() - 1970;
	return `${years} ${__('Years(s)')} ${age.getMonth()} ${__('Month(s)')} ${age.getDate()} ${__('Day(s)')}`;
};
