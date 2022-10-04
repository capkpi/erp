# Copyright (c) 2020, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	if capkpi.db.exists("DocType", "Issue"):
		capkpi.reload_doc("support", "doctype", "issue")
		rename_status()


def rename_status():
	capkpi.db.sql(
		"""
		UPDATE
			`tabIssue`
		SET
			status = 'On Hold'
		WHERE
			status = 'Hold'
	"""
	)
