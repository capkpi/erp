# Copyright (c) 2018, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

from erp.setup.doctype.company.company import install_country_fixtures


def execute():
	capkpi.reload_doc("regional", "report", "fichier_des_ecritures_comptables_[fec]")
	for d in capkpi.get_all("Company", filters={"country": "France"}):
		install_country_fixtures(d.name)
