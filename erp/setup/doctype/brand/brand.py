# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import copy

import capkpi
from capkpi.model.document import Document


class Brand(Document):
	pass


def get_brand_defaults(item, company):
	item = capkpi.get_cached_doc("Item", item)
	if item.brand:
		brand = capkpi.get_cached_doc("Brand", item.brand)

		for d in brand.brand_defaults or []:
			if d.company == company:
				row = copy.deepcopy(d.as_dict())
				row.pop("name")
				return row

	return capkpi._dict()
