import capkpi

from erp.setup.install import create_default_success_action


def execute():
	capkpi.reload_doc("core", "doctype", "success_action")
	create_default_success_action()
