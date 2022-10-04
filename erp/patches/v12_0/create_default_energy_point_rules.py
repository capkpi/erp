import capkpi

from erp.setup.install import create_default_energy_point_rules


def execute():
	capkpi.reload_doc("social", "doctype", "energy_point_rule")
	create_default_energy_point_rules()
