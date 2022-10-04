# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class Crop(Document):
	def validate(self):
		self.validate_crop_tasks()

	def validate_crop_tasks(self):
		for task in self.agriculture_task:
			if task.start_day > task.end_day:
				capkpi.throw(_("Start day is greater than end day in task '{0}'").format(task.task_name))

		# Verify that the crop period is correct
		max_crop_period = max([task.end_day for task in self.agriculture_task])
		self.period = max(self.period, max_crop_period)

		# Sort the crop tasks based on start days,
		# maintaining the order for same-day tasks
		self.agriculture_task.sort(key=lambda task: task.start_day)


@capkpi.whitelist()
def get_item_details(item_code):
	item = capkpi.get_doc("Item", item_code)
	return {"uom": item.stock_uom, "rate": item.valuation_rate}
