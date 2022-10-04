import capkpi


def execute():
	capkpi.reload_doc("support", "doctype", "issue_priority")
	capkpi.reload_doc("support", "doctype", "service_level_priority")
	capkpi.reload_doc("support", "doctype", "issue")

	set_issue_priority()
	set_priority_for_issue()
	set_priorities_service_level()
	set_priorities_service_level_agreement()


def set_issue_priority():
	# Adds priority from issue to Issue Priority DocType as Priority is a new DocType.
	for priority in capkpi.get_meta("Issue").get_field("priority").options.split("\n"):
		if priority and not capkpi.db.exists("Issue Priority", priority):
			capkpi.get_doc({"doctype": "Issue Priority", "name": priority}).insert(ignore_permissions=True)


def set_priority_for_issue():
	# Sets priority for Issues as Select field is changed to Link field.
	issue_priority = capkpi.get_list("Issue", fields=["name", "priority"])
	capkpi.reload_doc("support", "doctype", "issue")

	for issue in issue_priority:
		capkpi.db.set_value("Issue", issue.name, "priority", issue.priority)


def set_priorities_service_level():
	# Migrates "priority", "response_time", "response_time_period", "resolution_time", "resolution_time_period" to Child Table
	# as a Service Level can have multiple priorities
	try:
		service_level_priorities = capkpi.get_list(
			"Service Level",
			fields=[
				"name",
				"priority",
				"response_time",
				"response_time_period",
				"resolution_time",
				"resolution_time_period",
			],
		)

		capkpi.reload_doc("support", "doctype", "service_level")
		capkpi.reload_doc("support", "doctype", "support_settings")
		capkpi.db.set_value("Support Settings", None, "track_service_level_agreement", 1)

		for service_level in service_level_priorities:
			if service_level:
				doc = capkpi.get_doc("Service Level", service_level.name)
				if not doc.priorities:
					doc.append(
						"priorities",
						{
							"priority": service_level.priority,
							"default_priority": 1,
							"response_time": service_level.response_time,
							"response_time_period": service_level.response_time_period,
							"resolution_time": service_level.resolution_time,
							"resolution_time_period": service_level.resolution_time_period,
						},
					)
					doc.flags.ignore_validate = True
					doc.save(ignore_permissions=True)
	except capkpi.db.TableMissingError:
		capkpi.reload_doc("support", "doctype", "service_level")


def set_priorities_service_level_agreement():
	# Migrates "priority", "response_time", "response_time_period", "resolution_time", "resolution_time_period" to Child Table
	# as a Service Level Agreement can have multiple priorities
	try:
		service_level_agreement_priorities = capkpi.get_list(
			"Service Level Agreement",
			fields=[
				"name",
				"priority",
				"response_time",
				"response_time_period",
				"resolution_time",
				"resolution_time_period",
			],
		)

		capkpi.reload_doc("support", "doctype", "service_level_agreement")

		for service_level_agreement in service_level_agreement_priorities:
			if service_level_agreement:
				doc = capkpi.get_doc("Service Level Agreement", service_level_agreement.name)

				if doc.customer:
					doc.entity_type = "Customer"
					doc.entity = doc.customer

				doc.append(
					"priorities",
					{
						"priority": service_level_agreement.priority,
						"default_priority": 1,
						"response_time": service_level_agreement.response_time,
						"response_time_period": service_level_agreement.response_time_period,
						"resolution_time": service_level_agreement.resolution_time,
						"resolution_time_period": service_level_agreement.resolution_time_period,
					},
				)
				doc.flags.ignore_validate = True
				doc.save(ignore_permissions=True)
	except capkpi.db.TableMissingError:
		capkpi.reload_doc("support", "doctype", "service_level_agreement")
