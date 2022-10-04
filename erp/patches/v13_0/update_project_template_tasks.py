# Copyright (c) 2019, CapKPI and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.reload_doc("projects", "doctype", "project_template")
	capkpi.reload_doc("projects", "doctype", "project_template_task")
	capkpi.reload_doc("projects", "doctype", "task")

	# Update property setter status if any
	property_setter = capkpi.db.get_value(
		"Property Setter", {"doc_type": "Task", "field_name": "status", "property": "options"}
	)

	if property_setter:
		property_setter_doc = capkpi.get_doc(
			"Property Setter", {"doc_type": "Task", "field_name": "status", "property": "options"}
		)
		property_setter_doc.value += "\nTemplate"
		property_setter_doc.save()

	for template_name in capkpi.get_all("Project Template"):
		template = capkpi.get_doc("Project Template", template_name.name)
		replace_tasks = False
		new_tasks = []
		for task in template.tasks:
			if task.subject:
				replace_tasks = True
				new_task = capkpi.get_doc(
					dict(
						doctype="Task",
						subject=task.subject,
						start=task.start,
						duration=task.duration,
						task_weight=task.task_weight,
						description=task.description,
						is_template=1,
					)
				).insert()
				new_tasks.append(new_task)

		if replace_tasks:
			template.tasks = []
			for tsk in new_tasks:
				template.append("tasks", {"task": tsk.name, "subject": tsk.subject})
			template.save()
