import capkpi


def execute():
	capkpi.reload_doc("accounts", "doctype", "item_tax_template")

	item_tax_template_list = capkpi.get_list("Item Tax Template")
	for template in item_tax_template_list:
		doc = capkpi.get_doc("Item Tax Template", template.name)
		for tax in doc.taxes:
			doc.company = capkpi.get_value("Account", tax.tax_type, "company")
			break
		doc.save()
