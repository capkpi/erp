import capkpi
from capkpi.model.utils.rename_field import rename_field


def execute():
	capkpi.reload_doc("Healthcare", "doctype", "Inpatient Record")
	if capkpi.db.has_column("Inpatient Record", "discharge_ordered_date"):
		rename_field("Inpatient Record", "discharge_ordered_date", "discharge_ordered_datetime")
