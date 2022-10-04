import capkpi
from capkpi.model.utils.rename_field import rename_field
from capkpi.modules import get_doctype_module, scrub

field_rename_map = {
	"Patient Encounter": [
		["consultation_time", "encounter_time"],
		["consultation_date", "encounter_date"],
		["consultation_comment", "encounter_comment"],
		["physician", "practitioner"],
	],
	"Fee Validity": [["physician", "practitioner"]],
	"Lab Test": [["physician", "practitioner"]],
	"Patient Appointment": [
		["physician", "practitioner"],
		["referring_physician", "referring_practitioner"],
	],
	"Procedure Prescription": [["physician", "practitioner"]],
}

doc_rename_map = {
	"Physician Schedule Time Slot": "Healthcare Schedule Time Slot",
	"Physician Schedule": "Practitioner Schedule",
	"Physician Service Unit Schedule": "Practitioner Service Unit Schedule",
	"Consultation": "Patient Encounter",
	"Physician": "Healthcare Practitioner",
}


def execute():
	for dt in doc_rename_map:
		if capkpi.db.exists("DocType", dt):
			capkpi.rename_doc("DocType", dt, doc_rename_map[dt], force=True)

	for dn in field_rename_map:
		if capkpi.db.exists("DocType", dn):
			capkpi.reload_doc(get_doctype_module(dn), "doctype", scrub(dn))

	for dt, field_list in field_rename_map.items():
		if capkpi.db.exists("DocType", dt):
			for field in field_list:
				if capkpi.db.has_column(dt, field[0]):
					rename_field(dt, field[0], field[1])

	if capkpi.db.exists("DocType", "Practitioner Service Unit Schedule"):
		if capkpi.db.has_column("Practitioner Service Unit Schedule", "parentfield"):
			capkpi.db.sql(
				"""
				update `tabPractitioner Service Unit Schedule` set parentfield = 'practitioner_schedules'
				where parentfield = 'physician_schedules' and parenttype = 'Healthcare Practitioner'
			"""
			)

	if capkpi.db.exists("DocType", "Healthcare Practitioner"):
		capkpi.reload_doc("healthcare", "doctype", "healthcare_practitioner")
		capkpi.reload_doc("healthcare", "doctype", "practitioner_service_unit_schedule")
		if capkpi.db.has_column("Healthcare Practitioner", "physician_schedule"):
			for doc in capkpi.get_all("Healthcare Practitioner"):
				_doc = capkpi.get_doc("Healthcare Practitioner", doc.name)
				if _doc.physician_schedule:
					_doc.append("practitioner_schedules", {"schedule": _doc.physician_schedule})
					_doc.save()
