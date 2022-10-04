# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class CashFlowMapping(Document):
	def validate(self):
		self.validate_checked_options()

	def validate_checked_options(self):
		checked_fields = [
			d for d in self.meta.fields if d.fieldtype == "Check" and self.get(d.fieldname) == 1
		]
		if len(checked_fields) > 1:
			capkpi.throw(
				capkpi._("You can only select a maximum of one option from the list of check boxes."),
				title="Error",
			)
