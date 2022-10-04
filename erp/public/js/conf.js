// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.provide('erp');

// preferred modules for breadcrumbs
$.extend(capkpi.breadcrumbs.preferred, {
	"Item Group": "Stock",
	"Customer Group": "Selling",
	"Supplier Group": "Buying",
	"Territory": "Selling",
	"Sales Person": "Selling",
	"Sales Partner": "Selling",
	"Brand": "Stock",
	"Maintenance Schedule": "Support",
	"Maintenance Visit": "Support"
});

$.extend(capkpi.breadcrumbs.module_map, {
	'ERP Integrations': 'Integrations',
	'Geo': 'Settings',
	'Portal': 'Website',
	'Utilities': 'Settings',
	'E-commerce': 'Website',
	'Contacts': 'CRM'
});
