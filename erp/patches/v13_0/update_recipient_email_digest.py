# Copyright (c) 2020, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("setup", "doctype", "Email Digest")
	capkpi.reload_doc("setup", "doctype", "Email Digest Recipient")
	email_digests = capkpi.db.get_list("Email Digest", fields=["name", "recipient_list"])
	for email_digest in email_digests:
		if email_digest.recipient_list:
			for recipient in email_digest.recipient_list.split("\n"):
				if capkpi.db.exists("User", recipient):
					doc = capkpi.get_doc(
						{
							"doctype": "Email Digest Recipient",
							"parenttype": "Email Digest",
							"parentfield": "recipients",
							"parent": email_digest.name,
							"recipient": recipient,
						}
					)
					doc.insert()
