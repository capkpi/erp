capkpi.provide('capkpi.dashboards.chart_sources');

capkpi.dashboards.chart_sources["Department wise Patient Appointments"] = {
	method: "erp.healthcare.dashboard_chart_source.department_wise_patient_appointments.department_wise_patient_appointments.get",
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
