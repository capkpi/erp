import capkpi


def get_context(context):
	context.no_cache = True
	chapter = capkpi.get_doc("Chapter", capkpi.form_dict.name)
	if capkpi.session.user != "Guest":
		if capkpi.session.user in [d.user for d in chapter.members if d.enabled == 1]:
			context.already_member = True
		else:
			if capkpi.request.method == "GET":
				pass
			elif capkpi.request.method == "POST":
				chapter.append(
					"members",
					dict(
						user=capkpi.session.user,
						introduction=capkpi.form_dict.introduction,
						website_url=capkpi.form_dict.website_url,
						enabled=1,
					),
				)
				chapter.save(ignore_permissions=1)
				capkpi.db.commit()

	context.chapter = chapter
