# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.utils import set_request
from capkpi.website.render import render


class TestHomepage(unittest.TestCase):
	def test_homepage_load(self):
		set_request(method="GET", path="home")
		response = render()

		self.assertEqual(response.status_code, 200)

		html = capkpi.safe_decode(response.get_data())
		self.assertTrue('<section class="hero-section' in html)
