# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.model.document import Document


class PractitionerSchedule(Document):
	def autoname(self):
		self.name = self.schedule_name