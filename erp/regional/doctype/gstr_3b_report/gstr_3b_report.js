// Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

capkpi.ui.form.on('GSTR 3B Report', {
	refresh : function(frm) {
		frm.doc.__unsaved = 1;
		if(!frm.is_new()) {
			frm.set_intro(__("Please save the report again to rebuild or update"));
			frm.add_custom_button(__('Download JSON'), function() {
				var w = window.open(
					capkpi.urllib.get_full_url(
						"/api/method/erp.regional.doctype.gstr_3b_report.gstr_3b_report.make_json?"
						+"name="+encodeURIComponent(frm.doc.name)));

				if(!w) {
					capkpi.msgprint(__("Please enable pop-ups")); return;
				}
			});
			frm.add_custom_button(__('View Form'), function() {
				capkpi.call({
					"method" : "erp.regional.doctype.gstr_3b_report.gstr_3b_report.view_report",
					"args" : {
						name : frm.doc.name,
					},
					"callback" : function(r){

						let data = r.message;

						capkpi.ui.get_print_settings(false, print_settings => {

							capkpi.render_grid({
								template: 'gstr_3b_report',
								title: __(this.doctype),
								print_settings: print_settings,
								data: data,
								columns:[]
							});
						});
					}
				});
			});
		}

		let current_year = new Date().getFullYear();
		let options = [current_year, current_year-1, current_year-2];
		frm.set_df_property('year', 'options', options);
	},

	setup: function(frm) {
		frm.set_query('company_address', function(doc) {
			if(!doc.company) {
				capkpi.throw(__('Please set Company'));
			}

			return {
				query: 'capkpi.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Company',
					link_name: doc.company
				}
			};
		});
	},
});
