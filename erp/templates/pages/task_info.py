import capkpi


def get_context(context):
	context.no_cache = 1

	task = capkpi.get_doc("Task", capkpi.form_dict.task)

	context.comments = capkpi.get_all(
		"Communication",
		filters={"reference_name": task.name, "comment_type": "comment"},
		fields=["subject", "sender_full_name", "communication_date"],
	)

	context.doc = task
