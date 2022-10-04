import capkpi


def execute():
	for dt, dn in (("Page", "Hub"), ("DocType", "Hub Settings"), ("DocType", "Hub Category")):
		capkpi.delete_doc(dt, dn, ignore_missing=True)

	if capkpi.db.exists("DocType", "Data Migration Plan"):
		data_migration_plans = capkpi.get_all("Data Migration Plan", filters={"module": "Hub Node"})
		for plan in data_migration_plans:
			plan_doc = capkpi.get_doc("Data Migration Plan", plan.name)
			for m in plan_doc.get("mappings"):
				capkpi.delete_doc("Data Migration Mapping", m.mapping, force=True)
			docs = capkpi.get_all("Data Migration Run", filters={"data_migration_plan": plan.name})
			for doc in docs:
				capkpi.delete_doc("Data Migration Run", doc.name)
			capkpi.delete_doc("Data Migration Plan", plan.name)
