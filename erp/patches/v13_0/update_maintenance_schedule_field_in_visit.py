import capkpi


def execute():
	capkpi.reload_doc("maintenance", "doctype", "maintenance_visit")

	# Updates the Maintenance Schedule link to fetch serial nos
	from capkpi.query_builder.functions import Coalesce

	mvp = capkpi.qb.DocType("Maintenance Visit Purpose")
	mv = capkpi.qb.DocType("Maintenance Visit")

	capkpi.qb.update(mv).join(mvp).on(mvp.parent == mv.name).set(
		mv.maintenance_schedule, Coalesce(mvp.prevdoc_docname, "")
	).where(
		(mv.maintenance_type == "Scheduled") & (mvp.prevdoc_docname.notnull()) & (mv.docstatus < 2)
	).run(
		as_dict=1
	)
