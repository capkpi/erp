# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class PatientMedicalRecord(Document):
	def after_insert(self):
		if self.reference_doctype == "Patient Medical Record":
			capkpi.db.set_value("Patient Medical Record", self.name, "reference_name", self.name)
