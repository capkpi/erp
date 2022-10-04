# Copyright (c) 2017, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi

from erp.regional.italy.setup import add_permissions


def execute():
	countries = capkpi.get_all("Company", fields="country")
	countries = [country["country"] for country in countries]
	if "Italy" in countries:
		add_permissions()
