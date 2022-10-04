import capkpi


def execute():
	job = capkpi.db.exists("Scheduled Job Type", "patient_appointment.send_appointment_reminder")
	if job:
		method = (
			"erp.healthcare.doctype.patient_appointment.patient_appointment.send_appointment_reminder"
		)
		capkpi.db.set_value("Scheduled Job Type", job, "method", method)
