# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt
import unittest

import capkpi
from capkpi.core.doctype.user_permission.test_user_permission import create_user

from erp.e_commerce.doctype.website_item.website_item import make_website_item
from erp.e_commerce.doctype.wishlist.wishlist import add_to_wishlist, remove_from_wishlist
from erp.stock.doctype.item.test_item import make_item


class TestWishlist(unittest.TestCase):
	def setUp(self):
		item = make_item("Test Phone Series X")
		if not capkpi.db.exists("Website Item", {"item_code": "Test Phone Series X"}):
			make_website_item(item, save=True)

		item = make_item("Test Phone Series Y")
		if not capkpi.db.exists("Website Item", {"item_code": "Test Phone Series Y"}):
			make_website_item(item, save=True)

	def tearDown(self):
		capkpi.get_cached_doc("Website Item", {"item_code": "Test Phone Series X"}).delete()
		capkpi.get_cached_doc("Website Item", {"item_code": "Test Phone Series Y"}).delete()
		capkpi.get_cached_doc("Item", "Test Phone Series X").delete()
		capkpi.get_cached_doc("Item", "Test Phone Series Y").delete()

	def test_add_remove_items_in_wishlist(self):
		"Check if items are added and removed from user's wishlist."
		# add first item
		add_to_wishlist("Test Phone Series X")

		# check if wishlist was created and item was added
		self.assertTrue(capkpi.db.exists("Wishlist", {"user": capkpi.session.user}))
		self.assertTrue(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": capkpi.session.user}
			)
		)

		# add second item to wishlist
		add_to_wishlist("Test Phone Series Y")
		wishlist_length = capkpi.db.get_value(
			"Wishlist Item", {"parent": capkpi.session.user}, "count(*)"
		)
		self.assertEqual(wishlist_length, 2)

		remove_from_wishlist("Test Phone Series X")
		remove_from_wishlist("Test Phone Series Y")

		wishlist_length = capkpi.db.get_value(
			"Wishlist Item", {"parent": capkpi.session.user}, "count(*)"
		)
		self.assertIsNone(capkpi.db.exists("Wishlist Item", {"parent": capkpi.session.user}))
		self.assertEqual(wishlist_length, 0)

		# tear down
		capkpi.get_doc("Wishlist", {"user": capkpi.session.user}).delete()

	def test_add_remove_in_wishlist_multiple_users(self):
		"Check if items are added and removed from the correct user's wishlist."
		test_user = create_user("test_reviewer@example.com", "Customer")
		test_user_1 = create_user("test_reviewer_1@example.com", "Customer")

		# add to wishlist for first user
		capkpi.set_user(test_user.name)
		add_to_wishlist("Test Phone Series X")

		# add to wishlist for second user
		capkpi.set_user(test_user_1.name)
		add_to_wishlist("Test Phone Series X")

		# check wishlist and its content for users
		self.assertTrue(capkpi.db.exists("Wishlist", {"user": test_user.name}))
		self.assertTrue(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		self.assertTrue(capkpi.db.exists("Wishlist", {"user": test_user_1.name}))
		self.assertTrue(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user_1.name}
			)
		)

		# remove item for second user
		remove_from_wishlist("Test Phone Series X")

		# make sure item was removed for second user and not first
		self.assertFalse(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user_1.name}
			)
		)
		self.assertTrue(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		# remove item for first user
		capkpi.set_user(test_user.name)
		remove_from_wishlist("Test Phone Series X")
		self.assertFalse(
			capkpi.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		# tear down
		capkpi.set_user("Administrator")
		capkpi.get_doc("Wishlist", {"user": test_user.name}).delete()
		capkpi.get_doc("Wishlist", {"user": test_user_1.name}).delete()
