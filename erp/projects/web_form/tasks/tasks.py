import capkpi


def get_context(context):
	if capkpi.form_dict.project:
		context.parents = [
			{"title": capkpi.form_dict.project, "route": "/projects?project=" + capkpi.form_dict.project}
		]
		context.success_url = "/projects?project=" + capkpi.form_dict.project

	elif context.doc and context.doc.get("project"):
		context.parents = [
			{"title": context.doc.project, "route": "/projects?project=" + context.doc.project}
		]
		context.success_url = "/projects?project=" + context.doc.project
