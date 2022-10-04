import capkpi

from erp.regional.india import states


def execute():

	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	custom_fields = ["Address-gst_state", "Tax Category-gst_state"]

	# Update options in gst_state custom fields
	for field in custom_fields:
		if capkpi.db.exists("Custom Field", field):
			gst_state_field = capkpi.get_doc("Custom Field", field)
			gst_state_field.options = "\n".join(states)
			gst_state_field.save()
