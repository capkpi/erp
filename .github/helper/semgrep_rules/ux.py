import capkpi
from capkpi import _, msgprint, throw

# ruleid: capkpi-missing-translate-function-python
throw("Error Occured")

# ruleid: capkpi-missing-translate-function-python
capkpi.throw("Error Occured")

# ruleid: capkpi-missing-translate-function-python
capkpi.msgprint("Useful message")

# ruleid: capkpi-missing-translate-function-python
msgprint("Useful message")


# ok: capkpi-missing-translate-function-python
translatedmessage = _("Hello")

# ok: capkpi-missing-translate-function-python
throw(translatedmessage)

# ok: capkpi-missing-translate-function-python
msgprint(translatedmessage)

# ok: capkpi-missing-translate-function-python
msgprint(_("Helpful message"))

# ok: capkpi-missing-translate-function-python
capkpi.throw(_("Error occured"))
