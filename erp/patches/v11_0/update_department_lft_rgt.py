import capkpi
from capkpi import _
from capkpi.utils.nestedset import rebuild_tree


def execute():
	"""assign lft and rgt appropriately"""
	capkpi.reload_doc("hr", "doctype", "department")
	if not capkpi.db.exists("Department", _("All Departments")):
		capkpi.get_doc(
			{"doctype": "Department", "department_name": _("All Departments"), "is_group": 1}
		).insert(ignore_permissions=True, ignore_mandatory=True)

	capkpi.db.sql(
		"""update `tabDepartment` set parent_department = '{0}'
		where is_group = 0""".format(
			_("All Departments")
		)
	)

	rebuild_tree("Department", "parent_department")
