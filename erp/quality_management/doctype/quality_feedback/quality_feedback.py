# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class QualityFeedback(Document):
	@capkpi.whitelist()
	def set_parameters(self):
		if self.template and not getattr(self, "parameters", []):
			for d in capkpi.get_doc("Quality Feedback Template", self.template).parameters:
				self.append("parameters", dict(parameter=d.parameter, rating=1))

	def validate(self):
		if not self.document_name:
			self.document_type = "User"
			self.document_name = capkpi.session.user
		self.set_parameters()
