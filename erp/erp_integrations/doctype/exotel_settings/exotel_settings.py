# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
import requests
from capkpi import _
from capkpi.model.document import Document


class ExotelSettings(Document):
	def validate(self):
		self.verify_credentials()

	def verify_credentials(self):
		if self.enabled:
			response = requests.get(
				"https://api.exotel.com/v1/Accounts/{sid}".format(sid=self.account_sid),
				auth=(self.api_key, self.api_token),
			)
			if response.status_code != 200:
				capkpi.throw(_("Invalid credentials"))
