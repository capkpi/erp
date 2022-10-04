# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class ProjectType(Document):
	def on_trash(self):
		if self.name == "External":
			capkpi.throw(_("You cannot delete Project Type 'External'"))
