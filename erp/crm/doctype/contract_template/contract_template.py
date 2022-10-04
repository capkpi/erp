# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi.model.document import Document
from capkpi.utils.jinja import validate_template
from six import string_types


class ContractTemplate(Document):
	def validate(self):
		if self.contract_terms:
			validate_template(self.contract_terms)


@capkpi.whitelist()
def get_contract_template(template_name, doc):
	if isinstance(doc, string_types):
		doc = json.loads(doc)

	contract_template = capkpi.get_doc("Contract Template", template_name)
	contract_terms = None

	if contract_template.contract_terms:
		contract_terms = capkpi.render_template(contract_template.contract_terms, doc)

	return {"contract_template": contract_template, "contract_terms": contract_terms}
