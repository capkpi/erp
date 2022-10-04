# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi
from capkpi.tests.utils import CapKPITestCase

from erp.hr.doctype.employee.test_employee import make_employee
from erp.payroll.doctype.employee_tax_exemption_declaration.test_employee_tax_exemption_declaration import (
	create_exemption_category,
	create_payroll_period,
	setup_hra_exemption_prerequisites,
)


class TestEmployeeTaxExemptionProofSubmission(CapKPITestCase):
	def setUp(self):
		make_employee("employee@proofsubmission.com", company="_Test Company")
		create_payroll_period(company="_Test Company")
		create_exemption_category()
		capkpi.db.delete("Employee Tax Exemption Proof Submission")
		capkpi.db.delete("Salary Structure Assignment")

	def test_exemption_amount_lesser_than_category_max(self):
		proof = capkpi.get_doc(
			{
				"doctype": "Employee Tax Exemption Proof Submission",
				"employee": capkpi.get_value("Employee", {"user_id": "employee@proofsubmission.com"}, "name"),
				"payroll_period": "Test Payroll Period",
				"tax_exemption_proofs": [
					dict(
						exemption_sub_category="_Test Sub Category",
						type_of_proof="Test Proof",
						exemption_category="_Test Category",
						amount=150000,
					)
				],
			}
		)
		self.assertRaises(capkpi.ValidationError, proof.save)
		proof = capkpi.get_doc(
			{
				"doctype": "Employee Tax Exemption Proof Submission",
				"payroll_period": "Test Payroll Period",
				"employee": capkpi.get_value("Employee", {"user_id": "employee@proofsubmission.com"}, "name"),
				"tax_exemption_proofs": [
					dict(
						exemption_sub_category="_Test Sub Category",
						type_of_proof="Test Proof",
						exemption_category="_Test Category",
						amount=100000,
					)
				],
			}
		)
		self.assertTrue(proof.save)
		self.assertTrue(proof.submit)

	def test_duplicate_category_in_proof_submission(self):
		proof = capkpi.get_doc(
			{
				"doctype": "Employee Tax Exemption Proof Submission",
				"employee": capkpi.get_value("Employee", {"user_id": "employee@proofsubmission.com"}, "name"),
				"payroll_period": "Test Payroll Period",
				"tax_exemption_proofs": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						type_of_proof="Test Proof",
						amount=100000,
					),
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=50000,
					),
				],
			}
		)
		self.assertRaises(capkpi.ValidationError, proof.save)

	def test_india_hra_exemption(self):
		# set country
		current_country = capkpi.flags.country
		capkpi.flags.country = "India"

		employee = capkpi.get_value("Employee", {"user_id": "employee@proofsubmission.com"}, "name")
		setup_hra_exemption_prerequisites("Monthly", employee)
		payroll_period = capkpi.db.get_value(
			"Payroll Period", "_Test Payroll Period", ["start_date", "end_date"], as_dict=True
		)

		proof = capkpi.get_doc(
			{
				"doctype": "Employee Tax Exemption Proof Submission",
				"employee": employee,
				"company": "_Test Company",
				"payroll_period": "_Test Payroll Period",
				"currency": "INR",
				"house_rent_payment_amount": 600000,
				"rented_in_metro_city": 1,
				"rented_from_date": payroll_period.start_date,
				"rented_to_date": payroll_period.end_date,
				"tax_exemption_proofs": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						type_of_proof="Test Proof",
						amount=100000,
					),
					dict(
						exemption_sub_category="_Test1 Sub Category",
						exemption_category="_Test Category",
						type_of_proof="Test Proof",
						amount=50000,
					),
				],
			}
		).insert()

		self.assertEqual(proof.monthly_house_rent, 50000)

		# Monthly HRA received = 3000
		# should set HRA exemption as per actual annual HRA because that's the minimum
		self.assertEqual(proof.monthly_hra_exemption, 3000)
		self.assertEqual(proof.total_eligible_hra_exemption, 36000)

		# total exemptions + house rent payment amount
		self.assertEqual(proof.total_actual_amount, 750000)

		# 100000 Standard Exemption + 36000 HRA exemption
		self.assertEqual(proof.exemption_amount, 136000)

		# reset
		capkpi.flags.country = current_country
