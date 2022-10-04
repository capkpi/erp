capkpi.provide('erp.PointOfSale');

capkpi.pages['point-of-sale'].on_page_load = function(wrapper) {
	capkpi.ui.make_app_page({
		parent: wrapper,
		title: __('Point of Sale'),
		single_column: true
	});

	capkpi.require('assets/js/point-of-sale.min.js', function() {
		wrapper.pos = new erp.PointOfSale.Controller(wrapper);
		window.cur_pos = wrapper.pos;
	});
};

capkpi.pages['point-of-sale'].refresh = function(wrapper) {
	if (document.scannerDetectionData) {
		onScan.detachFrom(document);
		wrapper.pos.wrapper.html("");
		wrapper.pos.check_opening_entry();
	}
};
