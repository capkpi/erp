# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import capkpi
from capkpi import _, throw
from capkpi.model.document import Document
from capkpi.utils import cint
from capkpi.utils.jinja import validate_template
from six import string_types


class TermsandConditions(Document):
	def validate(self):
		if self.terms:
			validate_template(self.terms)
		if (
			not cint(self.buying)
			and not cint(self.selling)
			and not cint(self.hr)
			and not cint(self.disabled)
		):
			throw(_("At least one of the Applicable Modules should be selected"))


@capkpi.whitelist()
def get_terms_and_conditions(template_name, doc):
	if isinstance(doc, string_types):
		doc = json.loads(doc)

	terms_and_conditions = capkpi.get_doc("Terms and Conditions", template_name)

	if terms_and_conditions.terms:
		return capkpi.render_template(terms_and_conditions.terms, doc)
