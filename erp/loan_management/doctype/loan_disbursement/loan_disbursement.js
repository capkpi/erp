// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'erp/loan_management/loan_common.js' %};

capkpi.ui.form.on('Loan Disbursement', {
	refresh: function(frm) {
		frm.set_query('against_loan', function() {
			return {
				'filters': {
					'docstatus': 1,
					'status': 'Sanctioned'
				}
			}
		})
	}
});
