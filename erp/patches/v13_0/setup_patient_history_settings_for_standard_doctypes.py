import capkpi

from erp.healthcare.setup import setup_patient_history_settings


def execute():
	if "Healthcare" not in capkpi.get_active_domains():
		return

	capkpi.reload_doc("healthcare", "doctype", "Inpatient Medication Order")
	capkpi.reload_doc("healthcare", "doctype", "Therapy Session")
	capkpi.reload_doc("healthcare", "doctype", "Clinical Procedure")
	capkpi.reload_doc("healthcare", "doctype", "Patient History Settings")
	capkpi.reload_doc("healthcare", "doctype", "Patient History Standard Document Type")
	capkpi.reload_doc("healthcare", "doctype", "Patient History Custom Document Type")

	setup_patient_history_settings()
