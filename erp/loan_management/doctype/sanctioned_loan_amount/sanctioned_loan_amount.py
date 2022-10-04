# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class SanctionedLoanAmount(Document):
	def validate(self):
		sanctioned_doc = capkpi.db.exists(
			"Sanctioned Loan Amount", {"applicant": self.applicant, "company": self.company}
		)

		if sanctioned_doc and sanctioned_doc != self.name:
			capkpi.throw(
				_("Sanctioned Loan Amount already exists for {0} against company {1}").format(
					capkpi.bold(self.applicant), capkpi.bold(self.company)
				)
			)
