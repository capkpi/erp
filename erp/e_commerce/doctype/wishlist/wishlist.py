# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class Wishlist(Document):
	pass


@capkpi.whitelist()
def add_to_wishlist(item_code):
	"""Insert Item into wishlist."""

	if capkpi.db.exists("Wishlist Item", {"item_code": item_code, "parent": capkpi.session.user}):
		return

	web_item_data = capkpi.db.get_value(
		"Website Item",
		{"item_code": item_code},
		[
			"website_image",
			"website_warehouse",
			"name",
			"web_item_name",
			"item_name",
			"item_group",
			"route",
		],
		as_dict=1,
	)

	wished_item_dict = {
		"item_code": item_code,
		"item_name": web_item_data.get("item_name"),
		"item_group": web_item_data.get("item_group"),
		"website_item": web_item_data.get("name"),
		"web_item_name": web_item_data.get("web_item_name"),
		"image": web_item_data.get("website_image"),
		"warehouse": web_item_data.get("website_warehouse"),
		"route": web_item_data.get("route"),
	}

	if not capkpi.db.exists("Wishlist", capkpi.session.user):
		# initialise wishlist
		wishlist = capkpi.get_doc({"doctype": "Wishlist"})
		wishlist.user = capkpi.session.user
		wishlist.append("items", wished_item_dict)
		wishlist.save(ignore_permissions=True)
	else:
		wishlist = capkpi.get_doc("Wishlist", capkpi.session.user)
		item = wishlist.append("items", wished_item_dict)
		item.db_insert()

	if hasattr(capkpi.local, "cookie_manager"):
		capkpi.local.cookie_manager.set_cookie("wish_count", str(len(wishlist.items)))


@capkpi.whitelist()
def remove_from_wishlist(item_code):
	if capkpi.db.exists("Wishlist Item", {"item_code": item_code, "parent": capkpi.session.user}):
		capkpi.db.delete("Wishlist Item", {"item_code": item_code, "parent": capkpi.session.user})
		capkpi.db.commit()

		wishlist_items = capkpi.db.get_values("Wishlist Item", filters={"parent": capkpi.session.user})

		if hasattr(capkpi.local, "cookie_manager"):
			capkpi.local.cookie_manager.set_cookie("wish_count", str(len(wishlist_items)))
