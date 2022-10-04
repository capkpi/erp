import capkpi


def get_context(context):
	context.no_cache = True
	chapter = capkpi.get_doc("Chapter", capkpi.form_dict.name)
	context.member_deleted = True
	context.chapter = chapter
