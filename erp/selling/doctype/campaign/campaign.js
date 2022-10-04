// Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

capkpi.ui.form.on("Campaign", "refresh", function(frm) {
	erp.toggle_naming_series();
	if(frm.doc.__islocal) {
		frm.toggle_display("naming_series", capkpi.boot.sysdefaults.campaign_naming_by=="Naming Series");
	}
	else{
		cur_frm.add_custom_button(__("View Leads"), function() {
			capkpi.route_options = {"source": "Campaign","campaign_name": frm.doc.name}
			capkpi.set_route("List", "Lead");
		}, "fa fa-list", true);
	}
})
