capkpi.provide('capkpi.dashboards.chart_sources');

capkpi.dashboards.chart_sources["Account Balance Timeline"] = {
	method: "erp.accounts.dashboard_chart_source.account_balance_timeline.account_balance_timeline.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: capkpi.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "account",
			label: __("Account"),
			fieldtype: "Link",
			options: "Account",
			reqd: 1
		},
	]
};
