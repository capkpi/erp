capkpi.pages['organizational-chart'].on_page_load = function(wrapper) {
	capkpi.ui.make_app_page({
		parent: wrapper,
		title: __('Organizational Chart'),
		single_column: true
	});

	$(wrapper).bind('show', () => {
		capkpi.require('/assets/js/hierarchy-chart.min.js', () => {
			let organizational_chart = undefined;
			let method = 'erp.hr.page.organizational_chart.organizational_chart.get_children';

			if (capkpi.is_mobile()) {
				organizational_chart = new erp.HierarchyChartMobile('Employee', wrapper, method);
			} else {
				organizational_chart = new erp.HierarchyChart('Employee', wrapper, method);
			}

			capkpi.breadcrumbs.add('HR');
			organizational_chart.show();
		});
	});
};
