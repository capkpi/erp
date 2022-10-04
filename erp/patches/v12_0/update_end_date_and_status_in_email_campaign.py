import capkpi
from capkpi.utils import add_days, getdate, today


def execute():
	if capkpi.db.exists("DocType", "Email Campaign"):
		email_campaign = capkpi.get_all("Email Campaign")
		for campaign in email_campaign:
			doc = capkpi.get_doc("Email Campaign", campaign["name"])
			send_after_days = []

			camp = capkpi.get_doc("Campaign", doc.campaign_name)
			for entry in camp.get("campaign_schedules"):
				send_after_days.append(entry.send_after_days)
			if send_after_days:
				end_date = add_days(getdate(doc.start_date), max(send_after_days))
				doc.db_set("end_date", end_date)
			today_date = getdate(today())
			if doc.start_date > today_date:
				doc.db_set("status", "Scheduled")
			elif end_date >= today_date:
				doc.db_set("status", "In Progress")
			elif end_date < today_date:
				doc.db_set("status", "Completed")
