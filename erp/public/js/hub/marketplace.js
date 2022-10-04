import Vue from 'vue/dist/vue.js';
import './vue-plugins';

// components
import PageContainer from './PageContainer.vue';
import Sidebar from './Sidebar.vue';
import { ProfileDialog } from './components/profile_dialog';

// helpers
import './hub_call';

capkpi.provide('hub');
capkpi.provide('erp.hub');
capkpi.provide('capkpi.route');

capkpi.utils.make_event_emitter(capkpi.route);
capkpi.utils.make_event_emitter(erp.hub);

erp.hub.Marketplace = class Marketplace {
	constructor({ parent }) {
		this.$parent = $(parent);
		this.page = parent.page;

		this.update_hub_settings().then(() => {

			this.setup_header();
			this.make_sidebar();
			this.make_body();
			this.setup_events();
			this.refresh();

			if (!hub.is_server) {
				if (!hub.is_seller_registered()) {
					this.page.set_primary_action('Become a Seller', this.show_register_dialog.bind(this))
				} else {
					this.page.set_secondary_action('Add Users', this.show_add_user_dialog.bind(this));
				}
			}
		});
	}

	setup_header() {
		if (hub.is_server) return;
		this.page.set_title(__('Marketplace'));
	}

	setup_events() {
		this.$parent.on('click', '[data-route]', (e) => {
			const $target = $(e.currentTarget);
			const route = $target.data().route;
			capkpi.set_route(route);
		});

		// generic action handler
		this.$parent.on('click', '[data-action]', e => {
			const $target = $(e.currentTarget);
			const action = $target.data().action;

			if (action && this[action]) {
				this[action].apply(this, $target);
			}
		})
	}

	make_sidebar() {
		this.$sidebar = this.$parent.find('.layout-side-section').addClass('hidden-xs');

		new Vue({
			el: $('<div>').appendTo(this.$sidebar)[0],
			render: h => h(Sidebar)
		});
	}

	make_body() {
		this.$body = this.$parent.find('.layout-main-section');
		this.$page_container = $('<div class="hub-page-container">').appendTo(this.$body);

		new Vue({
			el: '.hub-page-container',
			render: h => h(PageContainer)
		});

		if (!hub.is_server) {
			erp.hub.on('seller-registered', () => {
				this.page.clear_primary_action();
			});
		}
	}

	refresh() {

	}

	show_register_dialog() {
		if(capkpi.session.user === 'Administrator') {
			capkpi.msgprint(__('You need to be a user other than Administrator with System Manager and Item Manager roles to register on Marketplace.'));
			return;
		}

		if (!is_subset(['System Manager', 'Item Manager'], capkpi.user_roles)) {
			capkpi.msgprint(__('You need to be a user with System Manager and Item Manager roles to register on Marketplace.'));
			return;
		}

		this.register_dialog = ProfileDialog(
			__('Become a Seller'),
			{
				label: __('Register'),
				on_submit: this.register_marketplace.bind(this)
			}
		);

		this.register_dialog.show();
	}

	register_marketplace({company, company_description}) {
		capkpi.call({
		    method: 'erp.hub_node.api.register_marketplace',
		    args: {
				company,
				company_description
			}
		}).then((r) => {
			if (r.message && r.message.ok) {
				this.register_dialog.hide();

				this.update_hub_settings()
					.then(() => {
						capkpi.set_route('marketplace', 'publish');
						erp.hub.trigger('seller-registered');
					});
			}
		});
	}

	show_add_user_dialog() {
		if (!is_subset(['System Manager', 'Item Manager'], capkpi.user_roles)) {
			capkpi.msgprint(__('You need to be a user with System Manager and Item Manager roles to add users to Marketplace.'));
			return;
		}

		this.get_unregistered_users()
			.then(r => {
				const user_list = r.message;

				const d = new capkpi.ui.Dialog({
					title: __('Add Users to Marketplace'),
					fields: [
						{
							label: __('Users'),
							fieldname: 'users',
							fieldtype: 'MultiSelect',
							reqd: 1,
							get_data() {
								return user_list;
							}
						}
					],
					primary_action({ users }) {
						const selected_users = users.split(',').map(d => d.trim()).filter(Boolean);

						if (!selected_users.every(user => user_list.includes(user))) {
							d.set_df_property('users', 'description', __('Some emails are invalid'));
							return;
						} else {
							d.set_df_property('users', 'description', '');
						}

						capkpi.call('erp.hub_node.api.register_users', {
							user_list: selected_users
						})
						.then(r => {
							d.hide();

							if (r.message && r.message.length) {
								capkpi.show_alert(__('Added {0} users', [r.message.length]));
							}
						});
					}
				});

				d.show();
			});
	}

	get_unregistered_users() {
		return capkpi.call('erp.hub_node.api.get_unregistered_users')
	}

	update_hub_settings() {
		return hub.get_settings().then(doc => {
			hub.settings = doc;
		});
	}
}

Object.assign(hub, {
	is_seller_registered() {
		return hub.settings.registered;
	},

	is_user_registered() {
		return this.is_seller_registered() && hub.settings.users
			.filter(hub_user => hub_user.user === capkpi.session.user)
			.length === 1;
	},

	get_settings() {
		if (capkpi.session.user === 'Guest') {
			return Promise.resolve({
				registered: 0
			});
		}
		return capkpi.db.get_doc('Marketplace Settings');
	}
});

/**
 * Returns true if list_a is subset of list_b
 * @param {Array} list_a
 * @param {Array} list_b
 */
function is_subset(list_a, list_b) {
	return list_a.every(item => list_b.includes(item));
}