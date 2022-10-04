# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import re

from capkpi.model.document import Document
from capkpi.model.naming import make_autoname


class RestaurantTable(Document):
	def autoname(self):
		prefix = re.sub("-+", "-", self.restaurant.replace(" ", "-"))
		self.name = make_autoname(prefix + "-.##")
