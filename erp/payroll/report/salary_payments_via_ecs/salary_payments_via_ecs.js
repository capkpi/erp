// Copyright (c) 2016, CapKPI Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

capkpi.require("assets/erp/js/salary_slip_deductions_report_filters.js", function() {

	let ecs_checklist_filter = erp.salary_slip_deductions_report_filters
	ecs_checklist_filter['filters'].push({
		fieldname: "type",
		label: __("Type"),
		fieldtype: "Select",
		options:["", "Bank", "Cash", "Cheque"]
	})

	capkpi.query_reports["Salary Payments via ECS"] = ecs_checklist_filter
});
