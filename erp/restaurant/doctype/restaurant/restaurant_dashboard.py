from capkpi import _


def get_data():
	return {
		"fieldname": "restaurant",
		"transactions": [
			{"label": _("Setup"), "items": ["Restaurant Menu", "Restaurant Table"]},
			{"label": _("Operations"), "items": ["Restaurant Reservation", "Sales Invoice"]},
		],
	}