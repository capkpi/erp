// Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.query_reports["GSTR-1"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": capkpi.defaults.get_user_default("Company")
		},
		{
			"fieldname": "company_address",
			"label": __("Address"),
			"fieldtype": "Link",
			"options": "Address",
			"get_query": function () {
				let company = capkpi.query_report.get_filter_value('company');
				if (company) {
					return {
						"query": 'capkpi.contacts.doctype.address.address.address_query',
						"filters": { link_doctype: 'Company', link_name: company }
					};
				}
			}
		},
		{
			"fieldname": "company_gstin",
			"label": __("Company GSTIN"),
			"fieldtype": "Select"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": capkpi.datetime.add_months(capkpi.datetime.get_today(), -3),
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": capkpi.datetime.get_today()
		},
		{
			"fieldname": "type_of_business",
			"label": __("Type of Business"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": [
				{ "value": "B2B", "label": __("B2B Invoices - 4A, 4B, 4C, 6B, 6C") },
				{ "value": "B2C Large", "label": __("B2C(Large) Invoices - 5A, 5B") },
				{ "value": "B2C Small", "label": __("B2C(Small) Invoices - 7") },
				{ "value": "CDNR-REG", "label": __("Credit/Debit Notes (Registered) - 9B") },
				{ "value": "CDNR-UNREG", "label": __("Credit/Debit Notes (Unregistered) - 9B") },
				{ "value": "EXPORT", "label": __("Export Invoice - 6A") },
				{ "value": "Advances", "label": __("Tax Liability (Advances Received) - 11A(1), 11A(2)") },
				{ "value": "NIL Rated", "label": __("NIL RATED/EXEMPTED Invoices") }
			],
			"default": "B2B"
		}
	],
	onload: function (report) {
		let filters = report.get_values();

		capkpi.call({
			method: 'erp.regional.report.gstr_1.gstr_1.get_company_gstins',
			args: {
				company: filters.company
			},
			callback: function(r) {
				capkpi.query_report.page.fields_dict.company_gstin.df.options = r.message;
				capkpi.query_report.page.fields_dict.company_gstin.refresh();
			}
		});

		report.page.add_inner_button(__("Download as JSON"), function () {
			let filters = report.get_values();

			capkpi.call({
				method: 'erp.regional.report.gstr_1.gstr_1.get_json',
				args: {
					data: report.data,
					report_name: report.report_name,
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						const args = {
							cmd: 'erp.regional.report.gstr_1.gstr_1.download_json_file',
							data: r.message.data,
							report_name: r.message.report_name,
							report_type: r.message.report_type
						};
						open_url_post(capkpi.request.url, args);
					}
				}
			});
		});
	}
}
