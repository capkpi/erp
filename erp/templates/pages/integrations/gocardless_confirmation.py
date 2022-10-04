# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import capkpi
from capkpi import _

from erp.erp_integrations.doctype.gocardless_settings.gocardless_settings import (
	get_gateway_controller,
	gocardless_initialization,
)

no_cache = 1

expected_keys = ("redirect_flow_id", "reference_doctype", "reference_docname")


def get_context(context):
	context.no_cache = 1

	# all these keys exist in form_dict
	if not (set(expected_keys) - set(capkpi.form_dict.keys())):
		for key in expected_keys:
			context[key] = capkpi.form_dict[key]

	else:
		capkpi.redirect_to_message(
			_("Some information is missing"),
			_("Looks like someone sent you to an incomplete URL. Please ask them to look into it."),
		)
		capkpi.local.flags.redirect_location = capkpi.local.response.location
		raise capkpi.Redirect


@capkpi.whitelist(allow_guest=True)
def confirm_payment(redirect_flow_id, reference_doctype, reference_docname):

	client = gocardless_initialization(reference_docname)

	try:
		redirect_flow = client.redirect_flows.complete(
			redirect_flow_id, params={"session_token": capkpi.session.user}
		)

		confirmation_url = redirect_flow.confirmation_url
		gocardless_success_page = capkpi.get_hooks("gocardless_success_page")
		if gocardless_success_page:
			confirmation_url = capkpi.get_attr(gocardless_success_page[-1])(
				reference_doctype, reference_docname
			)

		data = {
			"mandate": redirect_flow.links.mandate,
			"customer": redirect_flow.links.customer,
			"redirect_to": confirmation_url,
			"redirect_message": "Mandate successfully created",
			"reference_doctype": reference_doctype,
			"reference_docname": reference_docname,
		}

		try:
			create_mandate(data)
		except Exception as e:
			capkpi.log_error(e, "GoCardless Mandate Registration Error")

		gateway_controller = get_gateway_controller(reference_docname)
		capkpi.get_doc("GoCardless Settings", gateway_controller).create_payment_request(data)

		return {"redirect_to": confirmation_url}

	except Exception as e:
		capkpi.log_error(e, "GoCardless Payment Error")
		return {"redirect_to": "/integrations/payment-failed"}


def create_mandate(data):
	data = capkpi._dict(data)
	capkpi.logger().debug(data)

	mandate = data.get("mandate")

	if capkpi.db.exists("GoCardless Mandate", mandate):
		return

	else:
		reference_doc = capkpi.db.get_value(
			data.get("reference_doctype"),
			data.get("reference_docname"),
			["reference_doctype", "reference_name"],
			as_dict=1,
		)
		erp_customer = capkpi.db.get_value(
			reference_doc.reference_doctype, reference_doc.reference_name, ["customer_name"], as_dict=1
		)

		try:
			capkpi.get_doc(
				{
					"doctype": "GoCardless Mandate",
					"mandate": mandate,
					"customer": erp_customer.customer_name,
					"gocardless_customer": data.get("customer"),
				}
			).insert(ignore_permissions=True)

		except Exception:
			capkpi.log_error(capkpi.get_traceback())
