# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestTherapyType(unittest.TestCase):
	def test_therapy_type_item(self):
		therapy_type = create_therapy_type()
		self.assertTrue(capkpi.db.exists("Item", therapy_type.item))

		therapy_type.disabled = 1
		therapy_type.save()
		self.assertEqual(capkpi.db.get_value("Item", therapy_type.item, "disabled"), 1)


def create_therapy_type():
	exercise = create_exercise_type()
	therapy_type = capkpi.db.exists("Therapy Type", "Basic Rehab")
	if not therapy_type:
		therapy_type = capkpi.new_doc("Therapy Type")
		therapy_type.therapy_type = "Basic Rehab"
		therapy_type.default_duration = 30
		therapy_type.is_billable = 1
		therapy_type.rate = 5000
		therapy_type.item_code = "Basic Rehab"
		therapy_type.item_name = "Basic Rehab"
		therapy_type.item_group = "Services"
		therapy_type.append(
			"exercises",
			{"exercise_type": exercise.name, "counts_target": 10, "assistance_level": "Passive"},
		)
		therapy_type.save()
	else:
		therapy_type = capkpi.get_doc("Therapy Type", therapy_type)

	return therapy_type


def create_exercise_type():
	exercise_type = capkpi.db.exists("Exercise Type", "Sit to Stand")
	if not exercise_type:
		exercise_type = capkpi.new_doc("Exercise Type")
		exercise_type.exercise_name = "Sit to Stand"
		exercise_type.append("steps_table", {"title": "Step 1", "description": "Squat and Rise"})
		exercise_type.save()
	else:
		exercise_type = capkpi.get_doc("Exercise Type", exercise_type)

	return exercise_type
