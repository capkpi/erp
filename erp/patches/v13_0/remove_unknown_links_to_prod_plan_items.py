import capkpi


def execute():
	"""
	Remove "production_plan_item" field where linked field doesn't exist in tha table.
	"""
	capkpi.reload_doc("manufacturing", "doctype", "production_plan_item")

	work_order = capkpi.qb.DocType("Work Order")
	pp_item = capkpi.qb.DocType("Production Plan Item")

	broken_work_orders = (
		capkpi.qb.from_(work_order)
		.left_join(pp_item)
		.on(work_order.production_plan_item == pp_item.name)
		.select(work_order.name)
		.where(
			(work_order.docstatus == 0)
			& (work_order.production_plan_item.notnull())
			& (work_order.production_plan_item.like("new-production-plan%"))
			& (pp_item.name.isnull())
		)
	).run()

	if not broken_work_orders:
		return

	broken_work_order_names = [d[0] for d in broken_work_orders]

	(
		capkpi.qb.update(work_order)
		.set(work_order.production_plan_item, None)
		.where(work_order.name.isin(broken_work_order_names))
	).run()
