import capkpi

from erp.regional.india.setup import make_custom_fields


def execute():

	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	make_custom_fields()

	capkpi.reload_doctype("Tax Category")
	capkpi.reload_doctype("Sales Taxes and Charges Template")
	capkpi.reload_doctype("Purchase Taxes and Charges Template")

	# Create tax category with inter state field checked
	tax_category = capkpi.db.get_value("Tax Category", {"name": "OUT OF STATE"}, "name")

	if not tax_category:
		inter_state_category = capkpi.get_doc(
			{"doctype": "Tax Category", "title": "OUT OF STATE", "is_inter_state": 1}
		).insert()

		tax_category = inter_state_category.name

	for doctype in ("Sales Taxes and Charges Template", "Purchase Taxes and Charges Template"):
		if not capkpi.get_meta(doctype).has_field("is_inter_state"):
			continue

		template = capkpi.db.get_value(doctype, {"is_inter_state": 1, "disabled": 0}, ["name"])
		if template:
			capkpi.db.set_value(doctype, template, "tax_category", tax_category)

		capkpi.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname = 'is_inter_state'
			AND dt IN ('Sales Taxes and Charges Template', 'Purchase Taxes and Charges Template')
		"""
		)
