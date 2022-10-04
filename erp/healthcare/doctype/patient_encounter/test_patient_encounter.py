# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi

from erp.healthcare.doctype.patient_encounter.patient_encounter import PatientEncounter


class TestPatientEncounter(unittest.TestCase):
	def setUp(self):
		try:
			gender_m = capkpi.get_doc({"doctype": "Gender", "gender": "MALE"}).insert()
			gender_f = capkpi.get_doc({"doctype": "Gender", "gender": "FEMALE"}).insert()
		except capkpi.exceptions.DuplicateEntryError:
			gender_m = capkpi.get_doc({"doctype": "Gender", "gender": "MALE"})
			gender_f = capkpi.get_doc({"doctype": "Gender", "gender": "FEMALE"})

		self.patient_male = capkpi.get_doc(
			{
				"doctype": "Patient",
				"first_name": "John",
				"sex": gender_m.gender,
			}
		).insert()
		self.patient_female = capkpi.get_doc(
			{
				"doctype": "Patient",
				"first_name": "Curie",
				"sex": gender_f.gender,
			}
		).insert()
		self.practitioner = capkpi.get_doc(
			{
				"doctype": "Healthcare Practitioner",
				"first_name": "Doc",
				"sex": "MALE",
			}
		).insert()
		try:
			self.care_plan_male = capkpi.get_doc(
				{
					"doctype": "Treatment Plan Template",
					"template_name": "test plan - m",
					"gender": gender_m.gender,
				}
			).insert()
			self.care_plan_female = capkpi.get_doc(
				{
					"doctype": "Treatment Plan Template",
					"template_name": "test plan - f",
					"gender": gender_f.gender,
				}
			).insert()
		except capkpi.exceptions.DuplicateEntryError:
			self.care_plan_male = capkpi.get_doc(
				{
					"doctype": "Treatment Plan Template",
					"template_name": "test plan - m",
					"gender": gender_m.gender,
				}
			)
			self.care_plan_female = capkpi.get_doc(
				{
					"doctype": "Treatment Plan Template",
					"template_name": "test plan - f",
					"gender": gender_f.gender,
				}
			)

	def test_treatment_plan_template_filter(self):
		encounter = capkpi.get_doc(
			{
				"doctype": "Patient Encounter",
				"patient": self.patient_male.name,
				"practitioner": self.practitioner.name,
			}
		).insert()
		plans = PatientEncounter.get_applicable_treatment_plans(encounter.as_dict())
		self.assertEqual(plans[0]["name"], self.care_plan_male.template_name)

		encounter = capkpi.get_doc(
			{
				"doctype": "Patient Encounter",
				"patient": self.patient_female.name,
				"practitioner": self.practitioner.name,
			}
		).insert()
		plans = PatientEncounter.get_applicable_treatment_plans(encounter.as_dict())
		self.assertEqual(plans[0]["name"], self.care_plan_female.template_name)
