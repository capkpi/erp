# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


import capkpi
from dateutil.relativedelta import relativedelta
from capkpi.model.document import Document
from capkpi.utils import cint


class ManufacturingSettings(Document):
	pass


def get_mins_between_operations():
	return relativedelta(
		minutes=cint(capkpi.db.get_single_value("Manufacturing Settings", "mins_between_operations"))
		or 10
	)


@capkpi.whitelist()
def is_material_consumption_enabled():
	if not hasattr(capkpi.local, "material_consumption"):
		capkpi.local.material_consumption = cint(
			capkpi.db.get_single_value("Manufacturing Settings", "material_consumption")
		)

	return capkpi.local.material_consumption
