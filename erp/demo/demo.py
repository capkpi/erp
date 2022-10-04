import sys

import capkpi
import capkpi.utils

import erp
from erp.demo.setup import education, healthcare, manufacture, retail, setup_data
from erp.demo.user import accounts
from erp.demo.user import education as edu
from erp.demo.user import fixed_asset, hr, manufacturing, projects, purchase, sales, stock

"""
Make a demo

1. Start with a fresh account

bench --site demo.erp.dev reinstall

2. Install Demo

bench --site demo.erp.dev execute erp.demo.demo.make

3. If Demo breaks, to continue

bench --site demo.erp.dev execute erp.demo.demo.simulate

"""


def make(domain="Manufacturing", days=100):
	capkpi.flags.domain = domain
	capkpi.flags.mute_emails = True
	setup_data.setup(domain)
	if domain == "Manufacturing":
		manufacture.setup_data()
	elif domain == "Retail":
		retail.setup_data()
	elif domain == "Education":
		education.setup_data()
	elif domain == "Healthcare":
		healthcare.setup_data()

	site = capkpi.local.site
	capkpi.destroy()
	capkpi.init(site)
	capkpi.connect()

	simulate(domain, days)


def simulate(domain="Manufacturing", days=100):
	runs_for = capkpi.flags.runs_for or days
	capkpi.flags.company = erp.get_default_company()
	capkpi.flags.mute_emails = True

	if not capkpi.flags.start_date:
		# start date = 100 days back
		capkpi.flags.start_date = capkpi.utils.add_days(capkpi.utils.nowdate(), -1 * runs_for)

	current_date = capkpi.utils.getdate(capkpi.flags.start_date)

	# continue?
	demo_last_date = capkpi.db.get_global("demo_last_date")
	if demo_last_date:
		current_date = capkpi.utils.add_days(capkpi.utils.getdate(demo_last_date), 1)

	# run till today
	if not runs_for:
		runs_for = capkpi.utils.date_diff(capkpi.utils.nowdate(), current_date)
		# runs_for = 100

	fixed_asset.work()
	for i in range(runs_for):
		sys.stdout.write("\rSimulating {0}: Day {1}".format(current_date.strftime("%Y-%m-%d"), i))
		sys.stdout.flush()
		capkpi.flags.current_date = current_date
		if current_date.weekday() in (5, 6):
			current_date = capkpi.utils.add_days(current_date, 1)
			continue
		try:
			hr.work()
			purchase.work()
			stock.work()
			accounts.work()
			projects.run_projects(current_date)
			sales.work(domain)
			# run_messages()

			if domain == "Manufacturing":
				manufacturing.work()
			elif domain == "Education":
				edu.work()

		except Exception:
			capkpi.db.set_global("demo_last_date", current_date)
			raise
		finally:
			current_date = capkpi.utils.add_days(current_date, 1)
			capkpi.db.commit()
