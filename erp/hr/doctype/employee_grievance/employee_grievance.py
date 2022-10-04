# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import capkpi
from capkpi import _, bold
from capkpi.model.document import Document


class EmployeeGrievance(Document):
	def on_submit(self):
		if self.status not in ["Invalid", "Resolved"]:
			capkpi.throw(
				_("Only Employee Grievance with status {0} or {1} can be submitted").format(
					bold("Invalid"), bold("Resolved")
				)
			)
