import capkpi
from capkpi.utils.nestedset import rebuild_tree


def execute():
	capkpi.reload_doc("setup", "doctype", "company")
	rebuild_tree("Company", "parent_company")
