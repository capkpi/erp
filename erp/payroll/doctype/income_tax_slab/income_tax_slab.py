# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.model.document import Document

# import capkpi
import erp


class IncomeTaxSlab(Document):
	def validate(self):
		if self.company:
			self.currency = erp.get_company_currency(self.company)
