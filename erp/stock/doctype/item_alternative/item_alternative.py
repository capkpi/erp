# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class ItemAlternative(Document):
	def validate(self):
		self.has_alternative_item()
		self.validate_alternative_item()
		self.validate_duplicate()

	def has_alternative_item(self):
		if self.item_code and not capkpi.db.get_value("Item", self.item_code, "allow_alternative_item"):
			capkpi.throw(_("Not allow to set alternative item for the item {0}").format(self.item_code))

	def validate_alternative_item(self):
		if self.item_code == self.alternative_item_code:
			capkpi.throw(_("Alternative item must not be same as item code"))

		item_meta = capkpi.get_meta("Item")
		fields = [
			"is_stock_item",
			"include_item_in_manufacturing",
			"has_serial_no",
			"has_batch_no",
			"allow_alternative_item",
		]
		item_data = capkpi.db.get_value("Item", self.item_code, fields, as_dict=1)
		alternative_item_data = capkpi.db.get_value(
			"Item", self.alternative_item_code, fields, as_dict=1
		)

		for field in fields:
			if item_data.get(field) != alternative_item_data.get(field):
				raise_exception, alert = [1, False] if field == "is_stock_item" else [0, True]

				capkpi.msgprint(
					_("The value of {0} differs between Items {1} and {2}").format(
						capkpi.bold(item_meta.get_label(field)),
						capkpi.bold(self.alternative_item_code),
						capkpi.bold(self.item_code),
					),
					alert=alert,
					raise_exception=raise_exception,
					indicator="Orange",
				)

		alternate_item_check_msg = _("Allow Alternative Item must be checked on Item {}")

		if not item_data.allow_alternative_item:
			capkpi.throw(alternate_item_check_msg.format(self.item_code))
		if self.two_way and not alternative_item_data.allow_alternative_item:
			capkpi.throw(alternate_item_check_msg.format(self.item_code))

	def validate_duplicate(self):
		if capkpi.db.get_value(
			"Item Alternative",
			{
				"item_code": self.item_code,
				"alternative_item_code": self.alternative_item_code,
				"name": ("!=", self.name),
			},
		):
			capkpi.throw(_("Already record exists for the item {0}").format(self.item_code))


@capkpi.whitelist()
@capkpi.validate_and_sanitize_search_inputs
def get_alternative_items(doctype, txt, searchfield, start, page_len, filters):
	return capkpi.db.sql(
		""" (select alternative_item_code from `tabItem Alternative`
			where item_code = %(item_code)s and alternative_item_code like %(txt)s)
		union
			(select item_code from `tabItem Alternative`
			where alternative_item_code = %(item_code)s and item_code like %(txt)s
			and two_way = 1) limit {0}, {1}
		""".format(
			start, page_len
		),
		{"item_code": filters.get("item_code"), "txt": "%" + txt + "%"},
	)
