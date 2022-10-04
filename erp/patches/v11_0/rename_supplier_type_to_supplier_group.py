import capkpi
from capkpi import _
from capkpi.model.utils.rename_field import rename_field
from capkpi.utils.nestedset import rebuild_tree


def execute():
	if capkpi.db.table_exists("Supplier Group"):
		capkpi.reload_doc("setup", "doctype", "supplier_group")
	elif capkpi.db.table_exists("Supplier Type"):
		capkpi.rename_doc("DocType", "Supplier Type", "Supplier Group", force=True)
		capkpi.reload_doc("setup", "doctype", "supplier_group")
		capkpi.reload_doc("accounts", "doctype", "pricing_rule")
		capkpi.reload_doc("accounts", "doctype", "tax_rule")
		capkpi.reload_doc("buying", "doctype", "buying_settings")
		capkpi.reload_doc("buying", "doctype", "supplier")
		rename_field("Supplier Group", "supplier_type", "supplier_group_name")
		rename_field("Supplier", "supplier_type", "supplier_group")
		rename_field("Buying Settings", "supplier_type", "supplier_group")
		rename_field("Pricing Rule", "supplier_type", "supplier_group")
		rename_field("Tax Rule", "supplier_type", "supplier_group")

	build_tree()


def build_tree():
	capkpi.db.sql(
		"""update `tabSupplier Group` set parent_supplier_group = '{0}'
		where is_group = 0""".format(
			_("All Supplier Groups")
		)
	)

	if not capkpi.db.exists("Supplier Group", _("All Supplier Groups")):
		capkpi.get_doc(
			{
				"doctype": "Supplier Group",
				"supplier_group_name": _("All Supplier Groups"),
				"is_group": 1,
				"parent_supplier_group": "",
			}
		).insert(ignore_permissions=True)

	rebuild_tree("Supplier Group", "parent_supplier_group")
