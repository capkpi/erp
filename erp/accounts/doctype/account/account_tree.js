capkpi.provide("capkpi.treeview_settings")

capkpi.treeview_settings["Account"] = {
	breadcrumb: "Accounts",
	title: __("Chart of Accounts"),
	get_tree_root: false,
	filters: [
		{
			fieldname: "company",
			fieldtype:"Select",
			options: erp.utils.get_tree_options("company"),
			label: __("Company"),
			default: erp.utils.get_tree_default("company"),
			on_change: function() {
				var me = capkpi.treeview_settings['Account'].treeview;
				var company = me.page.fields_dict.company.get_value();
				if (!company) {
					capkpi.throw(__("Please set a Company"));
				}
				capkpi.call({
					method: "erp.accounts.doctype.account.account.get_root_company",
					args: {
						company: company,
					},
					callback: function(r) {
						if(r.message) {
							let root_company = r.message.length ? r.message[0] : "";
							me.page.fields_dict.root_company.set_value(root_company);

							capkpi.db.get_value("Company", {"name": company}, "allow_account_creation_against_child_company", (r) => {
								capkpi.flags.ignore_root_company_validation = r.allow_account_creation_against_child_company;
							});
						}
					}
				});
			}
		},
		{
			fieldname: "root_company",
			fieldtype:"Data",
			label: __("Root Company"),
			hidden: true,
			disable_onchange: true
		}
	],
	root_label: "Accounts",
	get_tree_nodes: 'erp.accounts.utils.get_children',
	on_get_node: function(nodes, deep=false) {
		if (capkpi.boot.user.can_read.indexOf("GL Entry") == -1) return;

		let accounts = [];
		if (deep) {
			// in case of `get_all_nodes`
			accounts = nodes.reduce((acc, node) => [...acc, ...node.data], []);
		} else {
			accounts = nodes;
		}

		const get_balances = capkpi.call({
			method: 'erp.accounts.utils.get_account_balances',
			args: {
				accounts: accounts,
				company: cur_tree.args.company
			},
		});

		get_balances.then(r => {
			if (!r.message || r.message.length == 0) return;

			for (let account of r.message) {

				const node = cur_tree.nodes && cur_tree.nodes[account.value];
				if (!node || node.is_root) continue;

				// show Dr if positive since balance is calculated as debit - credit else show Cr
				const balance = account.balance_in_account_currency || account.balance;
				const dr_or_cr = balance > 0 ? "Dr": "Cr";
				const format = (value, currency) => format_currency(Math.abs(value), currency);

				if (account.balance!==undefined) {
					node.parent && node.parent.find('.balance-area').remove();
					$('<span class="balance-area pull-right">'
						+ (account.balance_in_account_currency ?
							(format(account.balance_in_account_currency, account.account_currency) + " / ") : "")
						+ format(account.balance, account.company_currency)
						+ " " + dr_or_cr
						+ '</span>').insertBefore(node.$ul);
				}
			}
		});
	},
	add_tree_node: 'erp.accounts.utils.add_ac',
	menu_items:[
		{
			label: __('New Company'),
			action: function() { capkpi.new_doc("Company", true) },
			condition: 'capkpi.boot.user.can_create.indexOf("Company") !== -1'
		}
	],
	fields: [
		{fieldtype:'Data', fieldname:'account_name', label:__('New Account Name'), reqd:true,
			description: __("Name of new Account. Note: Please don't create accounts for Customers and Suppliers")},
		{fieldtype:'Data', fieldname:'account_number', label:__('Account Number'),
			description: __("Number of new Account, it will be included in the account name as a prefix")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
			description: __('Further accounts can be made under Groups, but entries can be made against non-Groups')},
		{fieldtype:'Select', fieldname:'root_type', label:__('Root Type'),
			options: ['Asset', 'Liability', 'Equity', 'Income', 'Expense'].join('\n'),
			depends_on: 'eval:doc.is_group && !doc.parent_account'},
		{fieldtype:'Select', fieldname:'account_type', label:__('Account Type'),
			options: capkpi.get_meta("Account").fields.filter(d => d.fieldname=='account_type')[0].options,
			description: __("Optional. This setting will be used to filter in various transactions.")
		},
		{fieldtype:'Float', fieldname:'tax_rate', label:__('Tax Rate'),
			depends_on: 'eval:doc.is_group==0&&doc.account_type=="Tax"'},
		{fieldtype:'Link', fieldname:'account_currency', label:__('Currency'), options:"Currency",
			description: __("Optional. Sets company's default currency, if not specified.")}
	],
	ignore_fields:["parent_account"],
	onload: function(treeview) {
		capkpi.treeview_settings['Account'].treeview = {};
		$.extend(capkpi.treeview_settings['Account'].treeview, treeview);
		function get_company() {
			return treeview.page.fields_dict.company.get_value();
		}

		// tools
		treeview.page.add_inner_button(__("Chart of Cost Centers"), function() {
			capkpi.set_route('Tree', 'Cost Center', {company: get_company()});
		}, __('View'));

		treeview.page.add_inner_button(__("Opening Invoice Creation Tool"), function() {
			capkpi.set_route('Form', 'Opening Invoice Creation Tool', {company: get_company()});
		}, __('View'));

		treeview.page.add_inner_button(__("Period Closing Voucher"), function() {
			capkpi.set_route('List', 'Period Closing Voucher', {company: get_company()});
		}, __('View'));


		treeview.page.add_inner_button(__("Journal Entry"), function() {
			capkpi.new_doc('Journal Entry', {company: get_company()});
		}, __('Create'));
		treeview.page.add_inner_button(__("Company"), function() {
			capkpi.new_doc('Company');
		}, __('Create'));

		// financial statements
		for (let report of ['Trial Balance', 'General Ledger', 'Balance Sheet',
			'Profit and Loss Statement', 'Cash Flow Statement', 'Accounts Payable', 'Accounts Receivable']) {
			treeview.page.add_inner_button(__(report), function() {
				capkpi.set_route('query-report', report, {company: get_company()});
			}, __('Financial Statements'));
		}

	},
	post_render: function(treeview) {
		capkpi.treeview_settings['Account'].treeview["tree"] = treeview.tree;
		treeview.page.set_primary_action(__("New"), function() {
			let root_company = treeview.page.fields_dict.root_company.get_value();

			if(root_company) {
				capkpi.throw(__("Please add the account to root level Company - ") + root_company);
			} else {
				treeview.new_node();
			}
		}, "add");
	},
	toolbar: [
		{
			label:__("Add Child"),
			condition: function(node) {
				return capkpi.boot.user.can_create.indexOf("Account") !== -1
					&& (!capkpi.treeview_settings['Account'].treeview.page.fields_dict.root_company.get_value()
					|| capkpi.flags.ignore_root_company_validation)
					&& node.expandable && !node.hide_add;
			},
			click: function() {
				var me = capkpi.views.trees['Account'];
				me.new_node();
			},
			btnClass: "hidden-xs"
		},
		{
			condition: function(node) {
				return !node.root && capkpi.boot.user.can_read.indexOf("GL Entry") !== -1
			},
			label: __("View Ledger"),
			click: function(node, btn) {
				capkpi.route_options = {
					"account": node.label,
					"from_date": capkpi.sys_defaults.year_start_date,
					"to_date": capkpi.sys_defaults.year_end_date,
					"company": capkpi.treeview_settings['Account'].treeview.page.fields_dict.company.get_value()
				};
				capkpi.set_route("query-report", "General Ledger");
			},
			btnClass: "hidden-xs"
		}
	],
	extend_toolbar: true
}
