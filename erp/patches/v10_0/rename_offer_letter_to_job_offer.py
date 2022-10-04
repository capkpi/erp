import capkpi


def execute():
	if capkpi.db.table_exists("Offer Letter") and not capkpi.db.table_exists("Job Offer"):
		capkpi.rename_doc("DocType", "Offer Letter", "Job Offer", force=True)
		capkpi.rename_doc("DocType", "Offer Letter Term", "Job Offer Term", force=True)
		capkpi.reload_doc("hr", "doctype", "job_offer")
		capkpi.reload_doc("hr", "doctype", "job_offer_term")
		capkpi.delete_doc("Print Format", "Offer Letter")
