# Copyright (c) 2015, CapKPI Technologies and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class PartyType(Document):
	pass


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_party_type(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	if filters and filters.get("account"):
		account_type = capkpi.db.get_value("Account", filters.get("account"), "account_type")
		cond = "and account_type = '%s'" % account_type

	return capkpi.db.sql(
		"""select name from `tabParty Type`
			where `{key}` LIKE %(txt)s {cond}
			order by name limit %(start)s, %(page_len)s""".format(
			key=searchfield, cond=cond
		),
		{"txt": "%" + txt + "%", "start": start, "page_len": page_len},
	)
