import capkpi
from capkpi import _

no_cache = 1


def get_context(context):
	if capkpi.session.user == "Guest":
		capkpi.throw(_("You need to be logged in to access this page"), capkpi.PermissionError)

	context.show_sidebar = True

	if capkpi.db.exists("Patient", {"email": capkpi.session.user}):
		patient = capkpi.get_doc("Patient", {"email": capkpi.session.user})
		context.doc = patient
		capkpi.form_dict.new = 0
		capkpi.form_dict.name = patient.name


def get_patient():
	return capkpi.get_value("Patient", {"email": capkpi.session.user}, "name")


def has_website_permission(doc, ptype, user, verbose=False):
	if doc.name == get_patient():
		return True
	else:
		return False
