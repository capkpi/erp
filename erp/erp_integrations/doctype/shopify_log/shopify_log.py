# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi.model.document import Document

from erp.erp_integrations.utils import get_webhook_address


class ShopifyLog(Document):
	pass


def make_shopify_log(status="Queued", exception=None, rollback=False):
	# if name not provided by log calling method then fetch existing queued state log
	make_new = False

	if not capkpi.flags.request_id:
		make_new = True

	if rollback:
		capkpi.db.rollback()

	if make_new:
		log = capkpi.get_doc({"doctype": "Shopify Log"}).insert(ignore_permissions=True)
	else:
		log = log = capkpi.get_doc("Shopify Log", capkpi.flags.request_id)

	log.message = get_message(exception)
	log.traceback = capkpi.get_traceback()
	log.status = status
	log.save(ignore_permissions=True)
	capkpi.db.commit()


def get_message(exception):
	message = None

	if hasattr(exception, "message"):
		message = exception.message
	elif hasattr(exception, "__str__"):
		message = exception.__str__()
	else:
		message = "Something went wrong while syncing"
	return message


def dump_request_data(data, event="create/order"):
	event_mapper = {
		"orders/create": get_webhook_address(
			connector_name="shopify_connection", method="sync_sales_order", exclude_uri=True
		),
		"orders/paid": get_webhook_address(
			connector_name="shopify_connection", method="prepare_sales_invoice", exclude_uri=True
		),
		"orders/fulfilled": get_webhook_address(
			connector_name="shopify_connection", method="prepare_delivery_note", exclude_uri=True
		),
	}

	log = capkpi.get_doc(
		{
			"doctype": "Shopify Log",
			"request_data": json.dumps(data, indent=1),
			"method": event_mapper[event],
		}
	).insert(ignore_permissions=True)

	capkpi.db.commit()
	capkpi.enqueue(
		method=event_mapper[event],
		queue="short",
		timeout=300,
		is_async=True,
		**{"order": data, "request_id": log.name}
	)


@capkpi.whitelist()
def resync(method, name, request_data):
	capkpi.db.set_value("Shopify Log", name, "status", "Queued", update_modified=False)
	if not method.startswith("erp.erp_integrations.connectors.shopify_connection"):
		return

	capkpi.enqueue(
		method=method,
		queue="short",
		timeout=300,
		is_async=True,
		**{"order": json.loads(request_data), "request_id": name}
	)