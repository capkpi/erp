# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class Weather(Document):
	@capkpi.whitelist()
	def load_contents(self):
		docs = capkpi.get_all("Agriculture Analysis Criteria", filters={"linked_doctype": "Weather"})
		for doc in docs:
			self.append("weather_parameter", {"title": str(doc.name)})
