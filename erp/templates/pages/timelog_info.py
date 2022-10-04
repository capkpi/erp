import capkpi


def get_context(context):
	context.no_cache = 1

	timelog = capkpi.get_doc("Time Log", capkpi.form_dict.timelog)

	context.doc = timelog
