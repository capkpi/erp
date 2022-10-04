# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document
from capkpi.website.utils import delete_page_cache


class Homepage(Document):
	def validate(self):
		if not self.description:
			self.description = capkpi._("This is an example website auto-generated from ERP")
		delete_page_cache("home")

	def setup_items(self):
		for d in capkpi.get_all(
			"Website Item",
			fields=["name", "item_name", "description", "website_image", "route"],
			filters={"published": 1},
			limit=3,
		):

			doc = capkpi.get_doc("Website Item", d.name)
			if not doc.route:
				# set missing route
				doc.save()
			self.append(
				"products",
				dict(
					item_code=d.name,
					item_name=d.item_name,
					description=d.description,
					image=d.website_image,
					route=d.route,
				),
			)
