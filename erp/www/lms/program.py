import capkpi
from capkpi import _

import erp.education.utils as utils

no_cache = 1


def get_context(context):
	try:
		program = capkpi.form_dict["program"]
	except KeyError:
		capkpi.local.flags.redirect_location = "/lms"
		raise capkpi.Redirect

	context.education_settings = capkpi.get_single("Education Settings")
	context.program = get_program(program)
	context.courses = [capkpi.get_doc("Course", course.course) for course in context.program.courses]
	context.has_access = utils.allowed_program_access(program)
	context.progress = get_course_progress(context.courses, context.program)


def get_program(program_name):
	try:
		return capkpi.get_doc("Program", program_name)
	except capkpi.DoesNotExistError:
		capkpi.throw(_("Program {0} does not exist.").format(program_name))


def get_course_progress(courses, program):
	progress = {course.name: utils.get_course_progress(course, program) for course in courses}
	return progress or {}
