import capkpi
from capkpi.email import sendmail_to_system_managers


def execute():
	capkpi.reload_doc("stock", "doctype", "item")
	capkpi.reload_doc("stock", "doctype", "customs_tariff_number")
	capkpi.reload_doc("accounts", "doctype", "payment_terms_template")
	capkpi.reload_doc("accounts", "doctype", "payment_schedule")

	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	capkpi.reload_doc("regional", "doctype", "gst_settings")
	capkpi.reload_doc("regional", "doctype", "gst_hsn_code")

	for report_name in (
		"GST Sales Register",
		"GST Purchase Register",
		"GST Itemised Sales Register",
		"GST Itemised Purchase Register",
	):

		capkpi.reload_doc("regional", "report", capkpi.scrub(report_name))

	from erp.regional.india.setup import setup

	delete_custom_field_tax_id_if_exists()
	setup(patch=True)
	send_gst_update_email()


def delete_custom_field_tax_id_if_exists():
	for field in capkpi.db.sql_list(
		"""select name from `tabCustom Field` where fieldname='tax_id'
		and dt in ('Sales Order', 'Sales Invoice', 'Delivery Note')"""
	):
		capkpi.delete_doc("Custom Field", field, ignore_permissions=True)
		capkpi.db.commit()


def send_gst_update_email():
	message = """Hello,

<p>ERP is now GST Ready!</p>

<p>To start making GST Invoices from 1st of July, you just need to create new Tax Accounts,
Templates and update your Customer's and Supplier's GST Numbers.</p>

<p>Please refer {gst_document_link} to know more about how to setup and implement GST in ERP.</p>

<p>Please contact us at support@capkpi.com, if you have any questions.</p>

<p>Thanks,</p>
ERP Team.
	""".format(
		gst_document_link="<a href='http://capkpi.github.io/erp/user/manual/en/regional/india/'> ERP GST Document </a>"
	)

	try:
		sendmail_to_system_managers("[Important] ERP GST updates", message)
	except Exception as e:
		pass
