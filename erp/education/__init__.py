import capkpi
from capkpi import _


class StudentNotInGroupError(capkpi.ValidationError):
	pass


def validate_student_belongs_to_group(student, student_group):
	groups = capkpi.db.get_all("Student Group Student", ["parent"], dict(student=student, active=1))
	if not student_group in [d.parent for d in groups]:
		capkpi.throw(
			_("Student {0} does not belong to group {1}").format(
				capkpi.bold(student), capkpi.bold(student_group)
			),
			StudentNotInGroupError,
		)
