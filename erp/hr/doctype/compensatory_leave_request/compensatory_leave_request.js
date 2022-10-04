// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('Compensatory Leave Request', {
	refresh: function(frm) {
		frm.set_query("leave_type", function() {
			return {
				filters: {
					"is_compensatory": true
				}
			};
		});
	},
	half_day: function(frm) {
		if(frm.doc.half_day == 1){
			frm.set_df_property('half_day_date', 'reqd', true);
		}
		else{
			frm.set_df_property('half_day_date', 'reqd', false);
		}
	}
});
