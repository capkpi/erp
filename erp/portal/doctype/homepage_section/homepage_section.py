# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from capkpi.model.document import Document
from capkpi.utils import cint


class HomepageSection(Document):
	@property
	def column_value(self):
		return cint(12 / cint(self.no_of_columns or 3))
