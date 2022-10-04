# Copyright (c) 2019, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class AppointmentLetter(Document):
	pass


@capkpi.whitelist()
def get_appointment_letter_details(template):
	body = []
	intro = capkpi.get_list(
		"Appointment Letter Template",
		fields=["introduction", "closing_notes"],
		filters={"name": template},
	)[0]
	content = capkpi.get_all(
		"Appointment Letter content",
		fields=["title", "description"],
		filters={"parent": template},
		order_by="idx",
	)
	body.append(intro)
	body.append({"description": content})
	return body
