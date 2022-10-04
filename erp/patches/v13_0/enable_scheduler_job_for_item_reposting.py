import capkpi


def execute():
	capkpi.reload_doc("core", "doctype", "scheduled_job_type")
	if capkpi.db.exists("Scheduled Job Type", "repost_item_valuation.repost_entries"):
		capkpi.db.set_value("Scheduled Job Type", "repost_item_valuation.repost_entries", "stopped", 0)
