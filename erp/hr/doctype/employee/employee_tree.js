capkpi.treeview_settings['Employee'] = {
	get_tree_nodes: "erp.hr.doctype.employee.employee.get_children",
	filters: [
		{
			fieldname: "company",
			fieldtype:"Select",
			options: ['All Companies'].concat(erp.utils.get_tree_options("company")),
			label: __("Company"),
			default: erp.utils.get_tree_default("company")
		}
	],
	breadcrumb: "Hr",
	disable_add_node: true,
	get_tree_root: false,
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				capkpi.set_route("Form", "Employee", node.data.value);
			}
		}
	],
	menu_items: [
		{
			label: __("New Employee"),
			action: function() {
				capkpi.new_doc("Employee", true);
			},
			condition: 'capkpi.boot.user.can_create.indexOf("Employee") !== -1'
		}
	],
};
