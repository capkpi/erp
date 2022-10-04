import capkpi
from dateutil.relativedelta import relativedelta
from capkpi.tests.utils import CapKPITestCase
from capkpi.utils import now_datetime

from erp.hr.doctype.attendance.attendance import mark_attendance
from erp.hr.doctype.employee.test_employee import make_employee
from erp.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute


class TestMonthlyAttendanceSheet(CapKPITestCase):
	def setUp(self):
		self.employee = make_employee("test_employee@example.com")
		capkpi.db.delete("Attendance", {"employee": self.employee})

	def test_monthly_attendance_sheet_report(self):
		now = now_datetime()
		previous_month = now.month - 1
		previous_month_first = now.replace(day=1).replace(month=previous_month).date()

		company = capkpi.db.get_value("Employee", self.employee, "company")

		# mark different attendance status on first 3 days of previous month
		mark_attendance(self.employee, previous_month_first, "Absent")
		mark_attendance(self.employee, previous_month_first + relativedelta(days=1), "Present")
		mark_attendance(self.employee, previous_month_first + relativedelta(days=2), "On Leave")

		filters = capkpi._dict(
			{
				"month": previous_month,
				"year": now.year,
				"company": company,
			}
		)
		report = execute(filters=filters)
		employees = report[1][0]
		datasets = report[3]["data"]["datasets"]
		absent = datasets[0]["values"]
		present = datasets[1]["values"]
		leaves = datasets[2]["values"]

		# ensure correct attendance is reflect on the report
		self.assertIn(self.employee, employees)
		self.assertEqual(absent[0], 1)
		self.assertEqual(present[1], 1)
		self.assertEqual(leaves[2], 1)
