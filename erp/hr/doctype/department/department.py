# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.utils.nestedset import NestedSet, get_root_of

from erp.utilities.transaction_base import delete_events


class Department(NestedSet):
	nsm_parent_field = "parent_department"

	def autoname(self):
		root = get_root_of("Department")
		if root and self.department_name != root:
			self.name = get_abbreviated_name(self.department_name, self.company)
		else:
			self.name = self.department_name

	def validate(self):
		if not self.parent_department:
			root = get_root_of("Department")
			if root:
				self.parent_department = root

	def before_rename(self, old, new, merge=False):
		# renaming consistency with abbreviation
		if not capkpi.get_cached_value("Company", self.company, "abbr") in new:
			new = get_abbreviated_name(new, self.company)

		return new

	def on_update(self):
		if not capkpi.local.flags.ignore_update_nsm:
			super(Department, self).on_update()

	def on_trash(self):
		super(Department, self).on_trash()
		delete_events(self.doctype, self.name)


def on_doctype_update():
	capkpi.db.add_index("Department", ["lft", "rgt"])


def get_abbreviated_name(name, company):
	abbr = capkpi.get_cached_value("Company", company, "abbr")
	new_name = "{0} - {1}".format(name, abbr)
	return new_name


@capkpi.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
	condition = ""
	var_dict = {
		"name": get_root_of("Department"),
		"parent": parent,
		"company": company,
	}
	if company == parent:
		condition = "name=%(name)s"
	elif company:
		condition = "parent_department=%(parent)s and company=%(company)s"
	else:
		condition = "parent_department = %(parent)s"

	return capkpi.db.sql(
		"""
		select
			name as value,
			is_group as expandable
		from `tab{doctype}`
		where
			{condition}
		order by name""".format(
			doctype=doctype, condition=condition
		),
		var_dict,
		as_dict=1,
	)


@capkpi.whitelist()
def add_node():
	from capkpi.desk.treeview import make_tree_args

	args = capkpi.form_dict
	args = make_tree_args(**args)

	if args.parent_department == args.company:
		args.parent_department = None

	capkpi.get_doc(args).insert()
