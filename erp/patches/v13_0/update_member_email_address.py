# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import capkpi
from capkpi.model.utils.rename_field import rename_field


def execute():
	"""add value to email_id column from email"""

	if capkpi.db.has_column("Member", "email"):
		# Get all members
		for member in capkpi.db.get_all("Member", pluck="name"):
			# Check if email_id already exists
			if not capkpi.db.get_value("Member", member, "email_id"):
				# fetch email id from the user linked field email
				email = capkpi.db.get_value("Member", member, "email")

				# Set the value for it
				capkpi.db.set_value("Member", member, "email_id", email)

	if capkpi.db.exists("DocType", "Membership Settings"):
		rename_field("Membership Settings", "enable_auto_invoicing", "enable_invoicing")
