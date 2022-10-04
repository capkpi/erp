# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.model.document import Document


class MedicalCode(Document):
	def autoname(self):
		self.name = self.medical_code_standard + " " + self.code
