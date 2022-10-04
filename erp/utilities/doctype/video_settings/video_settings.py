# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from apiclient.discovery import build
from capkpi import _
from capkpi.model.document import Document


class VideoSettings(Document):
	def validate(self):
		self.validate_youtube_api_key()

	def validate_youtube_api_key(self):
		if self.enable_youtube_tracking and self.api_key:
			try:
				build("youtube", "v3", developerKey=self.api_key)
			except Exception:
				title = _("Failed to Authenticate the API key.")
				capkpi.log_error(title + "\n\n" + capkpi.get_traceback(), title=title)
				capkpi.throw(title + " Please check the error logs.", title=_("Invalid Credentials"))
