# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class Operation(Document):
	def validate(self):
		if not self.description:
			self.description = self.name

		self.duplicate_sub_operation()
		self.set_total_time()

	def duplicate_sub_operation(self):
		operation_list = []
		for row in self.sub_operations:
			if row.operation in operation_list:
				capkpi.throw(
					_("The operation {0} can not add multiple times").format(capkpi.bold(row.operation))
				)

			if self.name == row.operation:
				capkpi.throw(
					_("The operation {0} can not be the sub operation").format(capkpi.bold(row.operation))
				)

			operation_list.append(row.operation)

	def set_total_time(self):
		self.total_operation_time = 0.0

		for row in self.sub_operations:
			self.total_operation_time += row.time_in_mins
