# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def get_context(context):
	project_user = capkpi.db.get_value(
		"Project User",
		{"parent": capkpi.form_dict.project, "user": capkpi.session.user},
		["user", "view_attachments"],
		as_dict=True,
	)
	if capkpi.session.user != "Administrator" and (
		not project_user or capkpi.session.user == "Guest"
	):
		raise capkpi.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	project = capkpi.get_doc("Project", capkpi.form_dict.project)

	project.has_permission("read")

	project.tasks = get_tasks(
		project.name, start=0, item_status="open", search=capkpi.form_dict.get("search")
	)

	project.timesheets = get_timesheets(project.name, start=0, search=capkpi.form_dict.get("search"))

	if project_user and project_user.view_attachments:
		project.attachments = get_attachments(project.name)

	context.doc = project


def get_tasks(project, start=0, search=None, item_status=None):
	filters = {"project": project}
	if search:
		filters["subject"] = ("like", "%{0}%".format(search))
	# if item_status:
	# 		filters["status"] = item_status
	tasks = capkpi.get_all(
		"Task",
		filters=filters,
		fields=[
			"name",
			"subject",
			"status",
			"modified",
			"_assign",
			"exp_end_date",
			"is_group",
			"parent_task",
		],
		limit_start=start,
		limit_page_length=10,
	)
	task_nest = []
	for task in tasks:
		if task.is_group:
			child_tasks = list(filter(lambda x: x.parent_task == task.name, tasks))
			if len(child_tasks):
				task.children = child_tasks
		task_nest.append(task)
	return list(filter(lambda x: not x.parent_task, tasks))


@capkpi.whitelist()
def get_task_html(project, start=0, item_status=None):
	return capkpi.render_template(
		"erp/templates/includes/projects/project_tasks.html",
		{
			"doc": {
				"name": project,
				"project_name": project,
				"tasks": get_tasks(project, start, item_status=item_status),
			}
		},
		is_path=True,
	)


def get_timesheets(project, start=0, search=None):
	filters = {"project": project}
	if search:
		filters["activity_type"] = ("like", "%{0}%".format(search))

	timesheets = capkpi.get_all(
		"Timesheet Detail",
		filters=filters,
		fields=["project", "activity_type", "from_time", "to_time", "parent"],
		limit_start=start,
		limit_page_length=10,
	)
	for timesheet in timesheets:
		info = capkpi.get_all(
			"Timesheet",
			filters={"name": timesheet.parent},
			fields=["name", "status", "modified", "modified_by"],
			limit_start=start,
			limit_page_length=10,
		)

		if len(info):
			timesheet.update(info[0])
	return timesheets


@capkpi.whitelist()
def get_timesheet_html(project, start=0):
	return capkpi.render_template(
		"erp/templates/includes/projects/project_timesheets.html",
		{"doc": {"timesheets": get_timesheets(project, start)}},
		is_path=True,
	)


def get_attachments(project):
	return capkpi.get_all(
		"File",
		filters={"attached_to_name": project, "attached_to_doctype": "Project", "is_private": 0},
		fields=["file_name", "file_url", "file_size"],
	)
