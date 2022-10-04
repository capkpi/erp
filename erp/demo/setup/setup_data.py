import json
import random

import capkpi
from capkpi import _
from capkpi.custom.doctype.custom_field.custom_field import create_custom_fields
from capkpi.utils import cstr, flt, now_datetime, random_string
from capkpi.utils.make_random import add_random_children, get_random
from capkpi.utils.nestedset import get_root_of

import erp
from erp.demo.domains import data


def setup(domain):
	capkpi.flags.in_demo = 1
	complete_setup(domain)
	setup_demo_page()
	setup_fiscal_year()
	setup_holiday_list()
	setup_user()
	setup_employee()
	setup_user_roles(domain)
	setup_role_permissions()
	setup_custom_field_for_domain()

	employees = capkpi.get_all("Employee", fields=["name", "date_of_joining"])

	# monthly salary
	setup_salary_structure(employees[:5], 0)

	# based on timesheet
	setup_salary_structure(employees[5:], 1)

	setup_leave_allocation()
	setup_customer()
	setup_supplier()
	setup_warehouse()
	import_json("Address")
	import_json("Contact")
	import_json("Lead")
	setup_currency_exchange()
	# setup_mode_of_payment()
	setup_account_to_expense_type()
	setup_budget()
	setup_pos_profile()

	capkpi.db.commit()
	capkpi.clear_cache()


def complete_setup(domain="Manufacturing"):
	print("Complete Setup...")
	from capkpi.desk.page.setup_wizard.setup_wizard import setup_complete

	if not capkpi.get_all("Company", limit=1):
		setup_complete(
			{
				"full_name": "Test User",
				"email": "test_demo@capkpi.com",
				"company_tagline": "Awesome Products and Services",
				"password": "demo",
				"fy_start_date": "2015-01-01",
				"fy_end_date": "2015-12-31",
				"bank_account": "National Bank",
				"domains": [domain],
				"company_name": data.get(domain).get("company_name"),
				"chart_of_accounts": "Standard",
				"company_abbr": "".join([d[0] for d in data.get(domain).get("company_name").split()]).upper(),
				"currency": "USD",
				"timezone": "America/New_York",
				"country": "United States",
				"language": "english",
			}
		)

		company = erp.get_default_company()

		if company:
			company_doc = capkpi.get_doc("Company", company)
			company_doc.db_set(
				"default_payroll_payable_account",
				capkpi.db.get_value("Account", dict(account_name="Payroll Payable")),
			)


def setup_demo_page():
	# home page should always be "start"
	website_settings = capkpi.get_doc("Website Settings", "Website Settings")
	website_settings.home_page = "demo"
	website_settings.save()


def setup_fiscal_year():
	fiscal_year = None
	for year in range(2010, now_datetime().year + 1, 1):
		try:
			fiscal_year = capkpi.get_doc(
				{
					"doctype": "Fiscal Year",
					"year": cstr(year),
					"year_start_date": "{0}-01-01".format(year),
					"year_end_date": "{0}-12-31".format(year),
				}
			).insert()
		except capkpi.DuplicateEntryError:
			pass

	# set the last fiscal year (current year) as default
	if fiscal_year:
		fiscal_year.set_as_default()


def setup_holiday_list():
	"""Setup Holiday List for the current year"""
	year = now_datetime().year
	holiday_list = capkpi.get_doc(
		{
			"doctype": "Holiday List",
			"holiday_list_name": str(year),
			"from_date": "{0}-01-01".format(year),
			"to_date": "{0}-12-31".format(year),
		}
	)
	holiday_list.insert()
	holiday_list.weekly_off = "Saturday"
	holiday_list.get_weekly_off_dates()
	holiday_list.weekly_off = "Sunday"
	holiday_list.get_weekly_off_dates()
	holiday_list.save()

	capkpi.set_value(
		"Company", erp.get_default_company(), "default_holiday_list", holiday_list.name
	)


def setup_user():
	capkpi.db.sql('delete from tabUser where name not in ("Guest", "Administrator")')
	for u in json.loads(open(capkpi.get_app_path("erp", "demo", "data", "user.json")).read()):
		user = capkpi.new_doc("User")
		user.update(u)
		user.flags.no_welcome_mail = True
		user.new_password = "Demo1234567!!!"
		user.insert()


def setup_employee():
	capkpi.db.set_value("HR Settings", None, "emp_created_by", "Naming Series")
	capkpi.db.commit()

	for d in capkpi.get_all("Salary Component"):
		salary_component = capkpi.get_doc("Salary Component", d.name)
		salary_component.append(
			"accounts",
			dict(
				company=erp.get_default_company(),
				account=capkpi.get_value("Account", dict(account_name=("like", "Salary%"))),
			),
		)
		salary_component.save()

	import_json("Employee")
	holiday_list = capkpi.db.get_value(
		"Holiday List", {"holiday_list_name": str(now_datetime().year)}, "name"
	)
	capkpi.db.sql("""update tabEmployee set holiday_list={0}""".format(holiday_list))


def setup_salary_structure(employees, salary_slip_based_on_timesheet=0):
	ss = capkpi.new_doc("Salary Structure")
	ss.name = "Sample Salary Structure - " + random_string(5)
	ss.salary_slip_based_on_timesheet = salary_slip_based_on_timesheet

	if salary_slip_based_on_timesheet:
		ss.salary_component = "Basic"
		ss.hour_rate = flt(random.random() * 10, 2)
	else:
		ss.payroll_frequency = "Monthly"

	ss.payment_account = capkpi.get_value(
		"Account",
		{"account_type": "Cash", "company": erp.get_default_company(), "is_group": 0},
		"name",
	)

	ss.append(
		"earnings",
		{
			"salary_component": "Basic",
			"abbr": "B",
			"formula": "base*.2",
			"amount_based_on_formula": 1,
			"idx": 1,
		},
	)
	ss.append(
		"deductions",
		{
			"salary_component": "Income Tax",
			"abbr": "IT",
			"condition": "base > 10000",
			"formula": "base*.1",
			"idx": 1,
		},
	)
	ss.insert()
	ss.submit()

	for e in employees:
		sa = capkpi.new_doc("Salary Structure Assignment")
		sa.employee = e.name
		sa.salary_structure = ss.name
		sa.from_date = "2015-01-01"
		sa.base = random.random() * 10000
		sa.insert()
		sa.submit()

	return ss


def setup_user_roles(domain):
	user = capkpi.get_doc("User", "demo@capkpi.com")
	user.add_roles(
		"HR User",
		"HR Manager",
		"Accounts User",
		"Accounts Manager",
		"Stock User",
		"Stock Manager",
		"Sales User",
		"Sales Manager",
		"Purchase User",
		"Purchase Manager",
		"Projects User",
		"Manufacturing User",
		"Manufacturing Manager",
		"Support Team",
	)

	if domain == "Healthcare":
		user.add_roles(
			"Physician", "Healthcare Administrator", "Laboratory User", "Nursing User", "Patient"
		)

	if domain == "Education":
		user.add_roles("Academics User")

	if not capkpi.db.get_global("demo_hr_user"):
		user = capkpi.get_doc("User", "CaitlinSnow@example.com")
		user.add_roles("HR User", "HR Manager", "Accounts User")
		capkpi.db.set_global("demo_hr_user", user.name)
		update_employee_department(user.name, "Human Resources")
		for d in capkpi.get_all("User Permission", filters={"user": "CaitlinSnow@example.com"}):
			capkpi.delete_doc("User Permission", d.name)

	if not capkpi.db.get_global("demo_sales_user_1"):
		user = capkpi.get_doc("User", "VandalSavage@example.com")
		user.add_roles("Sales User")
		update_employee_department(user.name, "Sales")
		capkpi.db.set_global("demo_sales_user_1", user.name)

	if not capkpi.db.get_global("demo_sales_user_2"):
		user = capkpi.get_doc("User", "GraceChoi@example.com")
		user.add_roles("Sales User", "Sales Manager", "Accounts User")
		update_employee_department(user.name, "Sales")
		capkpi.db.set_global("demo_sales_user_2", user.name)

	if not capkpi.db.get_global("demo_purchase_user"):
		user = capkpi.get_doc("User", "MaxwellLord@example.com")
		user.add_roles("Purchase User", "Purchase Manager", "Accounts User", "Stock User")
		update_employee_department(user.name, "Purchase")
		capkpi.db.set_global("demo_purchase_user", user.name)

	if not capkpi.db.get_global("demo_manufacturing_user"):
		user = capkpi.get_doc("User", "NeptuniaAquaria@example.com")
		user.add_roles(
			"Manufacturing User", "Stock Manager", "Stock User", "Purchase User", "Accounts User"
		)
		update_employee_department(user.name, "Production")
		capkpi.db.set_global("demo_manufacturing_user", user.name)

	if not capkpi.db.get_global("demo_stock_user"):
		user = capkpi.get_doc("User", "HollyGranger@example.com")
		user.add_roles("Manufacturing User", "Stock User", "Purchase User", "Accounts User")
		update_employee_department(user.name, "Production")
		capkpi.db.set_global("demo_stock_user", user.name)

	if not capkpi.db.get_global("demo_accounts_user"):
		user = capkpi.get_doc("User", "BarryAllen@example.com")
		user.add_roles("Accounts User", "Accounts Manager", "Sales User", "Purchase User")
		update_employee_department(user.name, "Accounts")
		capkpi.db.set_global("demo_accounts_user", user.name)

	if not capkpi.db.get_global("demo_projects_user"):
		user = capkpi.get_doc("User", "PeterParker@example.com")
		user.add_roles("HR User", "Projects User")
		update_employee_department(user.name, "Management")
		capkpi.db.set_global("demo_projects_user", user.name)

	if domain == "Education":
		if not capkpi.db.get_global("demo_education_user"):
			user = capkpi.get_doc("User", "ArthurCurry@example.com")
			user.add_roles("Academics User")
			update_employee_department(user.name, "Management")
			capkpi.db.set_global("demo_education_user", user.name)

	# Add Expense Approver
	user = capkpi.get_doc("User", "ClarkKent@example.com")
	user.add_roles("Expense Approver")


def setup_leave_allocation():
	year = now_datetime().year
	for employee in capkpi.get_all("Employee", fields=["name"]):
		leave_types = capkpi.get_all("Leave Type", fields=["name", "max_continuous_days_allowed"])
		for leave_type in leave_types:
			if not leave_type.max_continuous_days_allowed:
				leave_type.max_continuous_days_allowed = 10

		leave_allocation = capkpi.get_doc(
			{
				"doctype": "Leave Allocation",
				"employee": employee.name,
				"from_date": "{0}-01-01".format(year),
				"to_date": "{0}-12-31".format(year),
				"leave_type": leave_type.name,
				"new_leaves_allocated": random.randint(1, int(leave_type.max_continuous_days_allowed)),
			}
		)
		leave_allocation.insert()
		leave_allocation.submit()
		capkpi.db.commit()


def setup_customer():
	customers = [
		"Asian Junction",
		"Life Plan Counselling",
		"Two Pesos",
		"Mr Fables",
		"Intelacard",
		"Big D Supermarkets",
		"Adaptas",
		"Nelson Brothers",
		"Landskip Yard Care",
		"Buttrey Food & Drug",
		"Fayva",
		"Asian Fusion",
		"Crafts Canada",
		"Consumers and Consumers Express",
		"Netobill",
		"Choices",
		"Chi-Chis",
		"Red Food",
		"Endicott Shoes",
		"Hind Enterprises",
	]
	for c in customers:
		capkpi.get_doc(
			{
				"doctype": "Customer",
				"customer_name": c,
				"customer_group": "Commercial",
				"customer_type": random.choice(["Company", "Individual"]),
				"territory": "Rest Of The World",
			}
		).insert()


def setup_supplier():
	suppliers = [
		"Helios Air",
		"Ks Merchandise",
		"HomeBase",
		"Scott Ties",
		"Reliable Investments",
		"Nan Duskin",
		"Rainbow Records",
		"New World Realty",
		"Asiatic Solutions",
		"Eagle Hardware",
		"Modern Electricals",
	]
	for s in suppliers:
		capkpi.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": s,
				"supplier_group": random.choice(["Services", "Raw Material"]),
			}
		).insert()


def setup_warehouse():
	w = capkpi.new_doc("Warehouse")
	w.warehouse_name = "Supplier"
	w.insert()


def setup_currency_exchange():
	capkpi.get_doc(
		{
			"doctype": "Currency Exchange",
			"from_currency": "EUR",
			"to_currency": "USD",
			"exchange_rate": 1.13,
		}
	).insert()

	capkpi.get_doc(
		{
			"doctype": "Currency Exchange",
			"from_currency": "CNY",
			"to_currency": "USD",
			"exchange_rate": 0.16,
		}
	).insert()


def setup_mode_of_payment():
	company_abbr = capkpi.get_cached_value("Company", erp.get_default_company(), "abbr")
	account_dict = {"Cash": "Cash - " + company_abbr, "Bank": "National Bank - " + company_abbr}
	for payment_mode in capkpi.get_all("Mode of Payment", fields=["name", "type"]):
		if payment_mode.type:
			mop = capkpi.get_doc("Mode of Payment", payment_mode.name)
			mop.append(
				"accounts",
				{
					"company": erp.get_default_company(),
					"default_account": account_dict.get(payment_mode.type),
				},
			)
			mop.save(ignore_permissions=True)


def setup_account():
	capkpi.flags.in_import = True
	data = json.loads(open(capkpi.get_app_path("erp", "demo", "data", "account.json")).read())
	for d in data:
		doc = capkpi.new_doc("Account")
		doc.update(d)
		doc.parent_account = capkpi.db.get_value("Account", {"account_name": doc.parent_account})
		doc.insert()

	capkpi.flags.in_import = False


def setup_account_to_expense_type():
	company_abbr = capkpi.get_cached_value("Company", erp.get_default_company(), "abbr")
	expense_types = [
		{"name": _("Calls"), "account": "Sales Expenses - " + company_abbr},
		{"name": _("Food"), "account": "Entertainment Expenses - " + company_abbr},
		{"name": _("Medical"), "account": "Utility Expenses - " + company_abbr},
		{"name": _("Others"), "account": "Miscellaneous Expenses - " + company_abbr},
		{"name": _("Travel"), "account": "Travel Expenses - " + company_abbr},
	]

	for expense_type in expense_types:
		doc = capkpi.get_doc("Expense Claim Type", expense_type["name"])
		doc.append(
			"accounts",
			{"company": erp.get_default_company(), "default_account": expense_type["account"]},
		)
		doc.save(ignore_permissions=True)


def setup_budget():
	fiscal_years = capkpi.get_all("Fiscal Year", order_by="year_start_date")[-2:]

	for fy in fiscal_years:
		budget = capkpi.new_doc("Budget")
		budget.cost_center = get_random("Cost Center")
		budget.fiscal_year = fy.name
		budget.action_if_annual_budget_exceeded = "Warn"
		expense_ledger_count = capkpi.db.count("Account", {"is_group": "0", "root_type": "Expense"})

		add_random_children(
			budget,
			"accounts",
			rows=random.randint(10, expense_ledger_count),
			randomize={"account": ("Account", {"is_group": "0", "root_type": "Expense"})},
			unique="account",
		)

		for d in budget.accounts:
			d.budget_amount = random.randint(5, 100) * 10000

		budget.save()
		budget.submit()


def setup_pos_profile():
	company_abbr = capkpi.get_cached_value("Company", erp.get_default_company(), "abbr")
	pos = capkpi.new_doc("POS Profile")
	pos.user = capkpi.db.get_global("demo_accounts_user")
	pos.name = "Demo POS Profile"
	pos.naming_series = "SINV-"
	pos.update_stock = 0
	pos.write_off_account = "Cost of Goods Sold - " + company_abbr
	pos.write_off_cost_center = "Main - " + company_abbr
	pos.customer_group = get_root_of("Customer Group")
	pos.territory = get_root_of("Territory")

	pos.append(
		"payments",
		{
			"mode_of_payment": capkpi.db.get_value("Mode of Payment", {"type": "Cash"}, "name"),
			"amount": 0.0,
			"default": 1,
		},
	)

	pos.insert()


def setup_role_permissions():
	role_permissions = {"Batch": ["Accounts User", "Item Manager"]}
	for doctype, roles in role_permissions.items():
		for role in roles:
			if not capkpi.db.get_value("Custom DocPerm", {"parent": doctype, "role": role}):
				capkpi.get_doc(
					{
						"doctype": "Custom DocPerm",
						"role": role,
						"read": 1,
						"write": 1,
						"create": 1,
						"delete": 1,
						"parent": doctype,
					}
				).insert(ignore_permissions=True)


def import_json(doctype, submit=False, values=None):
	capkpi.flags.in_import = True
	data = json.loads(
		open(capkpi.get_app_path("erp", "demo", "data", capkpi.scrub(doctype) + ".json")).read()
	)
	for d in data:
		doc = capkpi.new_doc(doctype)
		doc.update(d)
		doc.insert()
		if submit:
			doc.submit()

	capkpi.db.commit()

	capkpi.flags.in_import = False


def update_employee_department(user_id, department):
	employee = capkpi.db.get_value("Employee", {"user_id": user_id}, "name")
	department = capkpi.db.get_value("Department", {"department_name": department}, "name")
	capkpi.db.set_value("Employee", employee, "department", department)


def setup_custom_field_for_domain():
	field = {
		"Item": [
			dict(
				fieldname="domain",
				label="Domain",
				fieldtype="Select",
				hidden=1,
				default="Manufacturing",
				options="Manufacturing\nService\nDistribution\nRetail",
			)
		]
	}
	create_custom_fields(field)
