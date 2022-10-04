import capkpi
from capkpi.utils import getdate, nowdate


def execute():
	capkpi.reload_doc("stock", "doctype", "serial_no")

	serial_no_list = capkpi.db.sql(
		"""select name, delivery_document_type, warranty_expiry_date, warehouse from `tabSerial No`
		where (status is NULL OR status='')""",
		as_dict=1,
	)
	if len(serial_no_list) > 20000:
		capkpi.db.auto_commit_on_many_writes = True

	for serial_no in serial_no_list:
		if serial_no.get("delivery_document_type"):
			status = "Delivered"
		elif serial_no.get("warranty_expiry_date") and getdate(
			serial_no.get("warranty_expiry_date")
		) <= getdate(nowdate()):
			status = "Expired"
		elif not serial_no.get("warehouse"):
			status = "Inactive"
		else:
			status = "Active"

		capkpi.db.set_value("Serial No", serial_no.get("name"), "status", status)

	if capkpi.db.auto_commit_on_many_writes:
		capkpi.db.auto_commit_on_many_writes = False
