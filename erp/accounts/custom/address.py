import capkpi
from capkpi import _
from capkpi.contacts.doctype.address.address import (
	Address,
	get_address_display,
	get_address_templates,
)


class ERPAddress(Address):
	def validate(self):
		self.validate_reference()
		super(ERPAddress, self).validate()

	def link_address(self):
		"""Link address based on owner"""
		if self.is_your_company_address:
			return

		return super(ERPAddress, self).link_address()

	def validate_reference(self):
		if self.is_your_company_address and not [
			row for row in self.links if row.link_doctype == "Company"
		]:
			capkpi.throw(
				_("Address needs to be linked to a Company. Please add a row for Company in the Links table."),
				title=_("Company Not Linked"),
			)

	def on_update(self):
		"""
		After Address is updated, update the related 'Primary Address' on Customer.
		"""
		address_display = get_address_display(self.as_dict())
		filters = {"customer_primary_address": self.name}
		customers = capkpi.db.get_all("Customer", filters=filters, as_list=True)
		for customer_name in customers:
			capkpi.db.set_value("Customer", customer_name[0], "primary_address", address_display)


@capkpi.whitelist()
def get_shipping_address(company, address=None):
	filters = [
		["Dynamic Link", "link_doctype", "=", "Company"],
		["Dynamic Link", "link_name", "=", company],
		["Address", "is_your_company_address", "=", 1],
	]
	fields = ["*"]
	if address and capkpi.db.get_value("Dynamic Link", {"parent": address, "link_name": company}):
		filters.append(["Address", "name", "=", address])
	if not address:
		filters.append(["Address", "is_shipping_address", "=", 1])

	address = capkpi.get_all("Address", filters=filters, fields=fields) or {}

	if address:
		address_as_dict = address[0]
		name, address_template = get_address_templates(address_as_dict)
		return address_as_dict.get("name"), capkpi.render_template(address_template, address_as_dict)
