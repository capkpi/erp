# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import _
from capkpi.utils import flt
from capkpi.utils.nestedset import NestedSet, get_root_of


class Territory(NestedSet):
	nsm_parent_field = "parent_territory"

	def validate(self):
		if not self.parent_territory:
			self.parent_territory = get_root_of("Territory")

		for d in self.get("targets") or []:
			if not flt(d.target_qty) and not flt(d.target_amount):
				capkpi.throw(_("Either target qty or target amount is mandatory"))

	def on_update(self):
		super(Territory, self).on_update()
		self.validate_one_root()


def on_doctype_update():
	capkpi.db.add_index("Territory", ["lft", "rgt"])
