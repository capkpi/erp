# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json
import os
import random

import capkpi
import capkpi.utils
from capkpi import _
from capkpi.utils.make_random import add_random_children


def make_sample_data(domains, make_dependent=False):
	"""Create a few opportunities, quotes, material requests, issues, todos, projects
	to help the user get started"""

	if make_dependent:
		items = capkpi.get_all("Item", {"is_sales_item": 1})
		customers = capkpi.get_all("Customer")
		warehouses = capkpi.get_all("Warehouse")

		if items and customers:
			for i in range(3):
				customer = random.choice(customers).name
				make_opportunity(items, customer)
				make_quote(items, customer)

		if items and warehouses:
			make_material_request(capkpi.get_all("Item"))

	make_projects(domains)
	import_notification()


def make_opportunity(items, customer):
	b = capkpi.get_doc(
		{
			"doctype": "Opportunity",
			"opportunity_from": "Customer",
			"customer": customer,
			"opportunity_type": _("Sales"),
			"with_items": 1,
		}
	)

	add_random_children(
		b, "items", rows=len(items), randomize={"qty": (1, 5), "item_code": ["Item"]}, unique="item_code"
	)

	b.insert(ignore_permissions=True)

	b.add_comment("Comment", text="This is a dummy record")


def make_quote(items, customer):
	qtn = capkpi.get_doc(
		{
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"party_name": customer,
			"order_type": "Sales",
		}
	)

	add_random_children(
		qtn,
		"items",
		rows=len(items),
		randomize={"qty": (1, 5), "item_code": ["Item"]},
		unique="item_code",
	)

	qtn.insert(ignore_permissions=True)

	qtn.add_comment("Comment", text="This is a dummy record")


def make_material_request(items):
	for i in items:
		mr = capkpi.get_doc(
			{
				"doctype": "Material Request",
				"material_request_type": "Purchase",
				"schedule_date": capkpi.utils.add_days(capkpi.utils.nowdate(), 7),
				"items": [
					{
						"schedule_date": capkpi.utils.add_days(capkpi.utils.nowdate(), 7),
						"item_code": i.name,
						"qty": 10,
					}
				],
			}
		)
		mr.insert()
		mr.submit()

		mr.add_comment("Comment", text="This is a dummy record")


def make_issue():
	pass


def make_projects(domains):
	current_date = capkpi.utils.nowdate()
	project = capkpi.get_doc(
		{
			"doctype": "Project",
			"project_name": "ERP Implementation",
		}
	)

	tasks = [
		{
			"title": "Explore ERP",
			"start_date": current_date,
			"end_date": current_date,
			"file": "explore.md",
		}
	]

	if "Education" in domains:
		tasks += [
			{
				"title": _("Setup your Institute in ERP"),
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 1),
				"file": "education_masters.md",
			},
			{
				"title": "Setup Master Data",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 1),
				"file": "education_masters.md",
			},
		]

	else:
		tasks += [
			{
				"title": "Setup Your Company",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 1),
				"file": "masters.md",
			},
			{
				"title": "Start Tracking your Sales",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 2),
				"file": "sales.md",
			},
			{
				"title": "Start Managing Purchases",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 3),
				"file": "purchase.md",
			},
			{
				"title": "Import Data",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 4),
				"file": "import_data.md",
			},
			{
				"title": "Go Live!",
				"start_date": current_date,
				"end_date": capkpi.utils.add_days(current_date, 5),
				"file": "go_live.md",
			},
		]

	for t in tasks:
		with open(os.path.join(os.path.dirname(__file__), "tasks", t["file"])) as f:
			t["description"] = capkpi.utils.md_to_html(f.read())
			del t["file"]

		project.append("tasks", t)

	project.insert(ignore_permissions=True)


def import_notification():
	"""Import notification for task start"""
	with open(os.path.join(os.path.dirname(__file__), "tasks/task_alert.json")) as f:
		notification = capkpi.get_doc(json.loads(f.read())[0])
		notification.insert()

	# trigger the first message!
	from capkpi.email.doctype.notification.notification import trigger_daily_alerts

	trigger_daily_alerts()


def test_sample():
	capkpi.db.sql("delete from `tabNotification`")
	capkpi.db.sql("delete from tabProject")
	capkpi.db.sql("delete from tabTask")
	make_projects("Education")
	import_notification()
