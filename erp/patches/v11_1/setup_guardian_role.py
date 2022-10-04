import capkpi


def execute():
	if "Education" in capkpi.get_active_domains() and not capkpi.db.exists("Role", "Guardian"):
		doc = capkpi.new_doc("Role")
		doc.update({"role_name": "Guardian", "desk_access": 0})

		doc.insert(ignore_permissions=True)
