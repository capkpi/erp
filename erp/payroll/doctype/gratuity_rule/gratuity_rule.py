# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class GratuityRule(Document):
	def validate(self):
		for current_slab in self.gratuity_rule_slabs:
			if (current_slab.from_year > current_slab.to_year) and current_slab.to_year != 0:
				capkpi.throw(
					_("Row {0}: From (Year) can not be greater than To (Year)").format(current_slab.idx)
				)

			if (
				current_slab.to_year == 0 and current_slab.from_year == 0 and len(self.gratuity_rule_slabs) > 1
			):
				capkpi.throw(
					_("You can not define multiple slabs if you have a slab with no lower and upper limits.")
				)


def get_gratuity_rule(name, slabs, **args):
	args = capkpi._dict(args)

	rule = capkpi.new_doc("Gratuity Rule")
	rule.name = name
	rule.calculate_gratuity_amount_based_on = (
		args.calculate_gratuity_amount_based_on or "Current Slab"
	)
	rule.work_experience_calculation_method = (
		args.work_experience_calculation_method or "Take Exact Completed Years"
	)
	rule.minimum_year_for_gratuity = 1

	for slab in slabs:
		slab = capkpi._dict(slab)
		rule.append("gratuity_rule_slabs", slab)
	return rule
