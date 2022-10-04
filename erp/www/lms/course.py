import capkpi

import erp.education.utils as utils

no_cache = 1


def get_context(context):
	try:
		program = capkpi.form_dict["program"]
		course_name = capkpi.form_dict["name"]
	except KeyError:
		capkpi.local.flags.redirect_location = "/lms"
		raise capkpi.Redirect

	context.education_settings = capkpi.get_single("Education Settings")
	course = capkpi.get_doc("Course", course_name)
	context.program = program
	context.course = course

	context.topics = course.get_topics()
	context.has_access = utils.allowed_program_access(context.program)
	context.progress = get_topic_progress(context.topics, course, context.program)


def get_topic_progress(topics, course, program):
	progress = {topic.name: utils.get_topic_progress(topic, course.name, program) for topic in topics}
	return progress
