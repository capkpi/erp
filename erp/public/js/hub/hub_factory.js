capkpi.provide('erp.hub');

capkpi.views.MarketplaceFactory = class MarketplaceFactory extends capkpi.views.Factory {
	show() {
		is_marketplace_disabled()
			.then(disabled => {
				if (disabled) {
					capkpi.show_not_found('Marketplace');
					return;
				}

				if (capkpi.pages.marketplace) {
					capkpi.container.change_to('marketplace');
					erp.hub.marketplace.refresh();
				} else {
					this.make('marketplace');
				}
			});
	}

	make(page_name) {
		const assets = [
			'/assets/js/marketplace.min.js'
		];

		capkpi.require(assets, () => {
			erp.hub.marketplace = new erp.hub.Marketplace({
				parent: this.make_page(true, page_name)
			});
		});
	}
};

function is_marketplace_disabled() {
	return capkpi.call({
		method: "erp.hub_node.doctype.marketplace_settings.marketplace_settings.is_marketplace_enabled"
	}).then(r => r.message)
}
