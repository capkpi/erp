# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi
from six import iteritems

from erp.setup.install import add_non_standard_user_types


def execute():
	doctype_dict = {
		"projects": ["Timesheet"],
		"payroll": [
			"Salary Slip",
			"Employee Tax Exemption Declaration",
			"Employee Tax Exemption Proof Submission",
		],
		"hr": [
			"Employee",
			"Expense Claim",
			"Leave Application",
			"Attendance Request",
			"Compensatory Leave Request",
		],
	}

	for module, doctypes in iteritems(doctype_dict):
		for doctype in doctypes:
			capkpi.reload_doc(module, "doctype", doctype)

	capkpi.flags.ignore_select_perm = True
	capkpi.flags.update_select_perm_after_migrate = True

	add_non_standard_user_types()
