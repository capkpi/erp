# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from capkpi import _


def get_data():
	return {
		"fieldname": "fee_structure",
		"transactions": [{"label": _("Fee"), "items": ["Fees", "Fee Schedule"]}],
	}
