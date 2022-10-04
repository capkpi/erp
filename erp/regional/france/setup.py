# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi.custom.doctype.custom_field.custom_field import create_custom_fields


def setup(company=None, patch=True):
	make_custom_fields()
	add_custom_roles_for_reports()


def make_custom_fields():
	custom_fields = {
		"Company": [
			dict(fieldname="siren_number", label="SIREN Number", fieldtype="Data", insert_after="website")
		]
	}

	create_custom_fields(custom_fields)


def add_custom_roles_for_reports():
	report_name = "Fichier des Ecritures Comptables [FEC]"

	if not capkpi.db.get_value("Custom Role", dict(report=report_name)):
		capkpi.get_doc(
			dict(doctype="Custom Role", report=report_name, roles=[dict(role="Accounts Manager")])
		).insert()
