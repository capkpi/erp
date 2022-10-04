# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.custom.doctype.custom_field.custom_field import create_custom_field
from capkpi.model.document import Document
from capkpi.utils.nestedset import get_root_of
from six.moves.urllib.parse import urlparse


class WoocommerceSettings(Document):
	def validate(self):
		self.validate_settings()
		self.create_delete_custom_fields()
		self.create_webhook_url()

	def create_delete_custom_fields(self):
		if self.enable_sync:
			custom_fields = {}
			# create
			for doctype in ["Customer", "Sales Order", "Item", "Address"]:
				df = dict(
					fieldname="woocommerce_id",
					label="Woocommerce ID",
					fieldtype="Data",
					read_only=1,
					print_hide=1,
				)
				create_custom_field(doctype, df)

			for doctype in ["Customer", "Address"]:
				df = dict(
					fieldname="woocommerce_email",
					label="Woocommerce Email",
					fieldtype="Data",
					read_only=1,
					print_hide=1,
				)
				create_custom_field(doctype, df)

			if not capkpi.get_value("Item Group", {"name": _("WooCommerce Products")}):
				item_group = capkpi.new_doc("Item Group")
				item_group.item_group_name = _("WooCommerce Products")
				item_group.parent_item_group = get_root_of("Item Group")
				item_group.insert()

	def validate_settings(self):
		if self.enable_sync:
			if not self.secret:
				self.set("secret", capkpi.generate_hash())

			if not self.woocommerce_server_url:
				capkpi.throw(_("Please enter Woocommerce Server URL"))

			if not self.api_consumer_key:
				capkpi.throw(_("Please enter API Consumer Key"))

			if not self.api_consumer_secret:
				capkpi.throw(_("Please enter API Consumer Secret"))

	def create_webhook_url(self):
		endpoint = "/api/method/erp.erp_integrations.connectors.woocommerce_connection.order"

		try:
			url = capkpi.request.url
		except RuntimeError:
			# for CI Test to work
			url = "http://localhost:8000"

		server_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))

		delivery_url = server_url + endpoint
		self.endpoint = delivery_url


@capkpi.whitelist()
def generate_secret():
	woocommerce_settings = capkpi.get_doc("Woocommerce Settings")
	woocommerce_settings.secret = capkpi.generate_hash()
	woocommerce_settings.save()


@capkpi.whitelist()
def get_series():
	return {
		"sales_order_series": capkpi.get_meta("Sales Order").get_options("naming_series") or "SO-WOO-",
	}
