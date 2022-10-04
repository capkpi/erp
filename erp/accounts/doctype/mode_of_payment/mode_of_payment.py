# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class ModeofPayment(Document):
	def validate(self):
		self.validate_accounts()
		self.validate_repeating_companies()
		self.validate_pos_mode_of_payment()

	def validate_repeating_companies(self):
		"""Error when Same Company is entered multiple times in accounts"""
		accounts_list = []
		for entry in self.accounts:
			accounts_list.append(entry.company)

		if len(accounts_list) != len(set(accounts_list)):
			capkpi.throw(_("Same Company is entered more than once"))

	def validate_accounts(self):
		for entry in self.accounts:
			"""Error when Company of Ledger account doesn't match with Company Selected"""
			if capkpi.db.get_value("Account", entry.default_account, "company") != entry.company:
				capkpi.throw(
					_("Account {0} does not match with Company {1} in Mode of Account: {2}").format(
						entry.default_account, entry.company, self.name
					)
				)

	def validate_pos_mode_of_payment(self):
		if not self.enabled:
			pos_profiles = capkpi.db.sql(
				"""SELECT sip.parent FROM `tabSales Invoice Payment` sip
				WHERE sip.parenttype = 'POS Profile' and sip.mode_of_payment = %s""",
				(self.name),
			)
			pos_profiles = list(map(lambda x: x[0], pos_profiles))

			if pos_profiles:
				message = (
					"POS Profile "
					+ capkpi.bold(", ".join(pos_profiles))
					+ " contains \
					Mode of Payment "
					+ capkpi.bold(str(self.name))
					+ ". Please remove them to disable this mode."
				)
				capkpi.throw(_(message), title="Not Allowed")
