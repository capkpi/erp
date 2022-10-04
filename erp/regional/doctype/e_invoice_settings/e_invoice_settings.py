# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import capkpi
from capkpi import _
from capkpi.model.document import Document


class EInvoiceSettings(Document):
	def validate(self):
		if self.enable and not self.credentials:
			capkpi.throw(_("You must add atleast one credentials to be able to use E Invoicing."))
