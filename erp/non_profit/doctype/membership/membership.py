# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json
from datetime import datetime

import capkpi
import six
from capkpi import _
from capkpi.email import sendmail_to_system_managers
from capkpi.model.document import Document
from capkpi.utils import add_days, add_months, add_years, get_link_to_form, getdate, nowdate

import erp
from erp import get_company_currency
from erp.non_profit.doctype.member.member import create_member


class Membership(Document):
	def validate(self):
		if not self.member or not capkpi.db.exists("Member", self.member):
			# for web forms
			user_type = capkpi.db.get_value("User", capkpi.session.user, "user_type")
			if user_type == "Website User":
				self.create_member_from_website_user()
			else:
				capkpi.throw(_("Please select a Member"))

		self.validate_membership_period()

	def create_member_from_website_user(self):
		member_name = capkpi.get_value("Member", dict(email_id=capkpi.session.user))

		if not member_name:
			user = capkpi.get_doc("User", capkpi.session.user)
			member = capkpi.get_doc(
				dict(
					doctype="Member",
					email_id=capkpi.session.user,
					membership_type=self.membership_type,
					member_name=user.get_fullname(),
				)
			).insert(ignore_permissions=True)
			member_name = member.name

		if self.get("__islocal"):
			self.member = member_name

	def validate_membership_period(self):
		# get last membership (if active)
		last_membership = erp.get_last_membership(self.member)

		# if person applied for offline membership
		if (
			last_membership
			and last_membership.name != self.name
			and not capkpi.session.user == "Administrator"
		):
			# if last membership does not expire in 30 days, then do not allow to renew
			if getdate(add_days(last_membership.to_date, -30)) > getdate(nowdate()):
				capkpi.throw(_("You can only renew if your membership expires within 30 days"))

			self.from_date = add_days(last_membership.to_date, 1)

		if capkpi.db.get_single_value("Non Profit Settings", "billing_cycle") == "Yearly":
			self.to_date = add_years(self.from_date, 1)
		else:
			self.to_date = add_months(self.from_date, 1)

	def on_payment_authorized(self, status_changed_to=None):
		if status_changed_to not in ("Completed", "Authorized"):
			return
		self.load_from_db()
		self.db_set("paid", 1)
		settings = capkpi.get_doc("Non Profit Settings")
		if settings.allow_invoicing and settings.automate_membership_invoicing:
			self.generate_invoice(
				with_payment_entry=settings.automate_membership_payment_entries, save=True
			)

	@capkpi.whitelist()
	def generate_invoice(self, save=True, with_payment_entry=False):
		if not (self.paid or self.currency or self.amount):
			capkpi.throw(
				_("The payment for this membership is not paid. To generate invoice fill the payment details")
			)

		if self.invoice:
			capkpi.throw(_("An invoice is already linked to this document"))

		member = capkpi.get_doc("Member", self.member)
		if not member.customer:
			capkpi.throw(_("No customer linked to member {0}").format(capkpi.bold(self.member)))

		plan = capkpi.get_doc("Membership Type", self.membership_type)
		settings = capkpi.get_doc("Non Profit Settings")
		self.validate_membership_type_and_settings(plan, settings)

		invoice = make_invoice(self, member, plan, settings)
		self.reload()
		self.invoice = invoice.name

		if with_payment_entry:
			self.make_payment_entry(settings, invoice)

		if save:
			self.save()

		return invoice

	def validate_membership_type_and_settings(self, plan, settings):
		settings_link = get_link_to_form("Non Profit Settings", "Non Profit Settings")

		if not settings.membership_debit_account:
			capkpi.throw(_("You need to set <b>Debit Account</b> in {0}").format(settings_link))

		if not settings.company:
			capkpi.throw(
				_("You need to set <b>Default Company</b> for invoicing in {0}").format(settings_link)
			)

		if not plan.linked_item:
			capkpi.throw(
				_("Please set a Linked Item for the Membership Type {0}").format(
					get_link_to_form("Membership Type", self.membership_type)
				)
			)

	def make_payment_entry(self, settings, invoice):
		if not settings.membership_payment_account:
			capkpi.throw(
				_("You need to set <b>Payment Account</b> for Membership in {0}").format(
					get_link_to_form("Non Profit Settings", "Non Profit Settings")
				)
			)

		from erp.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		capkpi.flags.ignore_account_permission = True
		pe = get_payment_entry(dt="Sales Invoice", dn=invoice.name, bank_amount=invoice.grand_total)
		capkpi.flags.ignore_account_permission = False
		pe.paid_to = settings.membership_payment_account
		pe.reference_no = self.name
		pe.reference_date = getdate()
		pe.flags.ignore_mandatory = True
		pe.save()
		pe.submit()

	@capkpi.whitelist()
	def send_acknowlement(self):
		settings = capkpi.get_doc("Non Profit Settings")
		if not settings.send_email:
			capkpi.throw(
				_("You need to enable <b>Send Acknowledge Email</b> in {0}").format(
					get_link_to_form("Non Profit Settings", "Non Profit Settings")
				)
			)

		member = capkpi.get_doc("Member", self.member)
		if not member.email_id:
			capkpi.throw(
				_("Email address of member {0} is missing").format(
					capkpi.utils.get_link_to_form("Member", self.member)
				)
			)

		plan = capkpi.get_doc("Membership Type", self.membership_type)
		email = member.email_id
		attachments = [
			capkpi.attach_print("Membership", self.name, print_format=settings.membership_print_format)
		]

		if self.invoice and settings.send_invoice:
			attachments.append(
				capkpi.attach_print("Sales Invoice", self.invoice, print_format=settings.inv_print_format)
			)

		email_template = capkpi.get_doc("Email Template", settings.email_template)
		context = {"doc": self, "member": member}

		email_args = {
			"recipients": [email],
			"message": capkpi.render_template(email_template.get("response"), context),
			"subject": capkpi.render_template(email_template.get("subject"), context),
			"attachments": attachments,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
		}

		if not capkpi.flags.in_test:
			capkpi.enqueue(method=capkpi.sendmail, queue="short", timeout=300, is_async=True, **email_args)
		else:
			capkpi.sendmail(**email_args)

	def generate_and_send_invoice(self):
		self.generate_invoice(save=False)
		self.send_acknowlement()


def make_invoice(membership, member, plan, settings):
	invoice = capkpi.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": member.customer,
			"debit_to": settings.membership_debit_account,
			"currency": membership.currency or get_company_currency(settings.company),
			"company": settings.company,
			"is_pos": 0,
			"items": [{"item_code": plan.linked_item, "rate": membership.amount, "qty": 1}],
		}
	)
	invoice.set_missing_values()
	invoice.insert()
	invoice.submit()

	capkpi.msgprint(_("Sales Invoice created successfully"))

	return invoice


def get_member_based_on_subscription(subscription_id, email=None, customer_id=None):
	filters = {"subscription_id": subscription_id}
	if email:
		filters.update({"email_id": email})
	if customer_id:
		filters.update({"customer_id": customer_id})

	members = capkpi.get_all("Member", filters=filters, order_by="creation desc")

	try:
		return capkpi.get_doc("Member", members[0]["name"])
	except Exception:
		return None


def verify_signature(data, endpoint="Membership"):
	signature = capkpi.request.headers.get("X-Razorpay-Signature")

	settings = capkpi.get_doc("Non Profit Settings")
	key = settings.get_webhook_secret(endpoint)

	controller = capkpi.get_doc("Razorpay Settings")

	controller.verify_signature(data, signature, key)
	capkpi.set_user(settings.creation_user)


@capkpi.whitelist(allow_guest=True)
def trigger_razorpay_subscription(*args, **kwargs):
	data = capkpi.request.get_data(as_text=True)
	data = process_request_data(data)

	subscription = data.payload.get("subscription", {}).get("entity", {})
	subscription = capkpi._dict(subscription)

	payment = data.payload.get("payment", {}).get("entity", {})
	payment = capkpi._dict(payment)

	try:
		if not data.event == "subscription.charged":
			return

		member = get_member_based_on_subscription(subscription.id, payment.email)
		if not member:
			member = create_member(
				capkpi._dict(
					{
						"fullname": payment.email,
						"email": payment.email,
						"plan_id": get_plan_from_razorpay_id(subscription.plan_id),
					}
				)
			)

			member.subscription_id = subscription.id
			member.customer_id = payment.customer_id

			if subscription.get("notes"):
				member = get_additional_notes(member, subscription)

		company = get_company_for_memberships()
		# Update Membership
		membership = capkpi.new_doc("Membership")
		membership.update(
			{
				"company": company,
				"member": member.name,
				"membership_status": "Current",
				"membership_type": member.membership_type,
				"currency": "INR",
				"paid": 1,
				"payment_id": payment.id,
				"from_date": datetime.fromtimestamp(subscription.current_start),
				"to_date": datetime.fromtimestamp(subscription.current_end),
				"amount": payment.amount / 100,  # Convert to rupees from paise
			}
		)
		membership.flags.ignore_mandatory = True
		membership.insert()

		# Update membership values
		member.subscription_start = datetime.fromtimestamp(subscription.start_at)
		member.subscription_end = datetime.fromtimestamp(subscription.end_at)
		member.subscription_status = "Active"
		member.flags.ignore_mandatory = True
		member.save()

		settings = capkpi.get_doc("Non Profit Settings")
		if settings.allow_invoicing and settings.automate_membership_invoicing:
			membership.reload()
			membership.generate_invoice(
				with_payment_entry=settings.automate_membership_payment_entries, save=True
			)

	except Exception as e:
		message = "{0}\n\n{1}\n\n{2}: {3}".format(e, capkpi.get_traceback(), _("Payment ID"), payment.id)
		log = capkpi.log_error(message, _("Error creating membership entry for {0}").format(member.name))
		notify_failure(log)
		return {"status": "Failed", "reason": e}

	return {"status": "Success"}


@capkpi.whitelist(allow_guest=True)
def update_halted_razorpay_subscription(*args, **kwargs):
	"""
	When all retries have been exhausted, Razorpay moves the subscription to the halted state.
	The customer has to manually retry the charge or change the card linked to the subscription,
	for the subscription to move back to the active state.
	"""
	if capkpi.request:
		data = capkpi.request.get_data(as_text=True)
		data = process_request_data(data)
	elif capkpi.flags.in_test:
		data = kwargs.get("data")
		data = capkpi._dict(data)
	else:
		return

	if not data.event == "subscription.halted":
		return

	subscription = data.payload.get("subscription", {}).get("entity", {})
	subscription = capkpi._dict(subscription)

	try:
		member = get_member_based_on_subscription(subscription.id, customer_id=subscription.customer_id)
		if not member:
			capkpi.throw(_("Member with Razorpay Subscription ID {0} not found").format(subscription.id))

		member.subscription_status = "Halted"
		member.flags.ignore_mandatory = True
		member.save()

		if subscription.get("notes"):
			member = get_additional_notes(member, subscription)

	except Exception as e:
		message = "{0}\n\n{1}".format(e, capkpi.get_traceback())
		log = capkpi.log_error(
			message, _("Error updating halted status for member {0}").format(member.name)
		)
		notify_failure(log)
		return {"status": "Failed", "reason": e}

	return {"status": "Success"}


def process_request_data(data):
	try:
		verify_signature(data)
	except Exception as e:
		log = capkpi.log_error(e, "Membership Webhook Verification Error")
		notify_failure(log)
		return {"status": "Failed", "reason": e}

	if isinstance(data, six.string_types):
		data = json.loads(data)
	data = capkpi._dict(data)

	return data


def get_company_for_memberships():
	company = capkpi.db.get_single_value("Non Profit Settings", "company")
	if not company:
		from erp.healthcare.setup import get_company

		company = get_company()
	return company


def get_additional_notes(member, subscription):
	if type(subscription.notes) == dict:
		for k, v in subscription.notes.items():
			notes = "\n".join("{}: {}".format(k, v))

			# extract member name from notes
			if "name" in k.lower():
				member.update({"member_name": subscription.notes.get(k)})

			# extract pan number from notes
			if "pan" in k.lower():
				member.update({"pan_number": subscription.notes.get(k)})

		member.add_comment("Comment", notes)

	elif type(subscription.notes) == str:
		member.add_comment("Comment", subscription.notes)

	return member


def notify_failure(log):
	try:
		content = """
			Dear System Manager,
			Razorpay webhook for creating renewing membership subscription failed due to some reason.
			Please check the following error log linked below
			Error Log: {0}
			Regards, Administrator
		""".format(
			get_link_to_form("Error Log", log.name)
		)

		sendmail_to_system_managers(
			"[Important] [ERP] Razorpay membership webhook failed , please check.", content
		)
	except Exception:
		pass


def get_plan_from_razorpay_id(plan_id):
	plan = capkpi.get_all(
		"Membership Type", filters={"razorpay_plan_id": plan_id}, order_by="creation desc"
	)

	try:
		return plan[0]["name"]
	except Exception:
		return None


def set_expired_status():
	capkpi.db.sql(
		"""
		UPDATE
			`tabMembership` SET `membership_status` = 'Expired'
		WHERE
			`membership_status` not in ('Cancelled') AND `to_date` < %s
		""",
		(nowdate()),
	)
