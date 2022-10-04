capkpi.provide('capkpi.dashboards.chart_sources');

capkpi.dashboards.chart_sources["Warehouse wise Stock Value"] = {
	method: "erp.stock.dashboard_chart_source.warehouse_wise_stock_value.warehouse_wise_stock_value.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: capkpi.defaults.get_user_default("Company")
		}
	]
};
