# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi import ValidationError

# test_records = capkpi.get_test_records('Bank Account')


class TestBankAccount(unittest.TestCase):
	def test_validate_iban(self):
		valid_ibans = [
			"GB82 WEST 1234 5698 7654 32",
			"DE91 1000 0000 0123 4567 89",
			"FR76 3000 6000 0112 3456 7890 189",
		]

		invalid_ibans = [
			# wrong checksum (3rd place)
			"GB72 WEST 1234 5698 7654 32",
			"DE81 1000 0000 0123 4567 89",
			"FR66 3000 6000 0112 3456 7890 189",
		]

		bank_account = capkpi.get_doc({"doctype": "Bank Account"})

		try:
			bank_account.validate_iban()
		except AttributeError:
			msg = "BankAccount.validate_iban() failed for empty IBAN"
			self.fail(msg=msg)

		for iban in valid_ibans:
			bank_account.iban = iban
			try:
				bank_account.validate_iban()
			except ValidationError:
				msg = "BankAccount.validate_iban() failed for valid IBAN {}".format(iban)
				self.fail(msg=msg)

		for not_iban in invalid_ibans:
			bank_account.iban = not_iban
			msg = "BankAccount.validate_iban() accepted invalid IBAN {}".format(not_iban)
			with self.assertRaises(ValidationError, msg=msg):
				bank_account.validate_iban()
