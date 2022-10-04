# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document
from capkpi.model.rename_doc import bulk_rename


class RenameTool(Document):
	pass


@capkpi.whitelist()
def get_doctypes():
	return capkpi.db.sql_list(
		"""select name from tabDocType
		where allow_rename=1 and module!='Core' order by name"""
	)


@capkpi.whitelist()
def upload(select_doctype=None, rows=None):
	from capkpi.utils.csvutils import read_csv_content_from_attached_file

	if not select_doctype:
		select_doctype = capkpi.form_dict.select_doctype

	if not capkpi.has_permission(select_doctype, "write"):
		raise capkpi.PermissionError

	rows = read_csv_content_from_attached_file(capkpi.get_doc("Rename Tool", "Rename Tool"))

	return bulk_rename(select_doctype, rows=rows)
