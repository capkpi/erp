import capkpi
from capkpi import _
from capkpi.model.document import Document


# ruleid: capkpi-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		capkpi.throw(_('Value of goods cannot be 0'))
	self.status = 'Submitted'


# ok: capkpi-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		capkpi.throw(_('Value of goods cannot be 0'))
	self.status = 'Submitted'
	self.db_set('status', 'Submitted')

# ok: capkpi-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		capkpi.throw(_('Value of goods cannot be 0'))
	x = "y"
	self.status = x
	self.db_set('status', x)


# ok: capkpi-modifying-but-not-comitting
def on_submit(self):
	x = "y"
	self.status = x
	self.save()

# ruleid: capkpi-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()

	def tainted_method(self):
		self.status = "uptate"


# ok: capkpi-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()

	def tainted_method(self):
		self.status = "update"
		self.db_set("status", "update")

# ok: capkpi-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()
		self.save()

	def tainted_method(self):
		self.status = "uptate"
