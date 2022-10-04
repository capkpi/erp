import capkpi

import erp.education.utils as utils

no_cache = 1


def get_context(context):
	# Load Query Parameters
	try:
		program = capkpi.form_dict["program"]
		content = capkpi.form_dict["content"]
		content_type = capkpi.form_dict["type"]
		course = capkpi.form_dict["course"]
		topic = capkpi.form_dict["topic"]
	except KeyError:
		capkpi.local.flags.redirect_location = "/lms"
		raise capkpi.Redirect

	# Check if user has access to the content
	has_program_access = utils.allowed_program_access(program)
	has_content_access = allowed_content_access(program, content, content_type)

	if capkpi.session.user == "Guest" or not has_program_access or not has_content_access:
		capkpi.local.flags.redirect_location = "/lms"
		raise capkpi.Redirect

	# Set context for content to be displayer
	context.content = capkpi.get_doc(content_type, content).as_dict()
	context.content_type = content_type
	context.program = program
	context.course = course
	context.topic = topic

	topic = capkpi.get_doc("Topic", topic)
	content_list = [
		{"content_type": item.content_type, "content": item.content} for item in topic.topic_content
	]

	# Set context for progress numbers
	context.position = content_list.index({"content": content, "content_type": content_type})
	context.length = len(content_list)

	# Set context for navigation
	context.previous = get_previous_content(content_list, context.position)
	context.next = get_next_content(content_list, context.position)


def get_next_content(content_list, current_index):
	try:
		return content_list[current_index + 1]
	except IndexError:
		return None


def get_previous_content(content_list, current_index):
	if current_index == 0:
		return None
	else:
		return content_list[current_index - 1]


def allowed_content_access(program, content, content_type):
	contents_of_program = capkpi.db.sql(
		"""select `tabTopic Content`.content, `tabTopic Content`.content_type
	from `tabCourse Topic`,
		 `tabProgram Course`,
		 `tabTopic Content`
	where `tabCourse Topic`.parent = `tabProgram Course`.course
			and `tabTopic Content`.parent = `tabCourse Topic`.topic
			and `tabProgram Course`.parent = %(program)s""",
		{"program": program},
	)

	return (content, content_type) in contents_of_program
