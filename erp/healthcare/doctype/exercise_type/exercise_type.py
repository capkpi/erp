# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


# import capkpi
from capkpi.model.document import Document


class ExerciseType(Document):
	def autoname(self):
		if self.difficulty_level:
			self.name = " - ".join(filter(None, [self.exercise_name, self.difficulty_level]))
		else:
			self.name = self.exercise_name
