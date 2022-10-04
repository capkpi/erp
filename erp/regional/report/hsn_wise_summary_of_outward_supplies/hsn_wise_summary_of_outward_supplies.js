// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

{% include "erp/regional/report/india_gst_common/india_gst_common.js" %}

capkpi.query_reports["HSN-wise-summary of outward supplies"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": capkpi.defaults.get_user_default("Company"),
			"on_change": fetch_gstins
		},
		{
			"fieldname":"gst_hsn_code",
			"label": __("HSN/SAC"),
			"fieldtype": "Link",
			"options": "GST HSN Code",
			"width": "80"
		},
		{
			"fieldname":"company_gstin",
			"label": __("Company GSTIN"),
			"fieldtype": "Select",
			"placeholder":"Company GSTIN",
			"options": [""],
			"width": "80"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80"
		},

	],
	onload: (report) => {
		fetch_gstins(report);

		report.page.add_inner_button(__("Download JSON"), function () {
			var filters = report.get_values();

			capkpi.call({
				method: 'erp.regional.report.hsn_wise_summary_of_outward_supplies.hsn_wise_summary_of_outward_supplies.get_json',
				args: {
					data: report.data,
					report_name: report.report_name,
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						const args = {
							cmd: 'erp.regional.report.hsn_wise_summary_of_outward_supplies.hsn_wise_summary_of_outward_supplies.download_json_file',
							data: r.message.data,
							report_name: r.message.report_name
						};
						open_url_post(capkpi.request.url, args);
					}
				}
			});
		});
	}
};
