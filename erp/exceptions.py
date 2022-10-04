import capkpi


# accounts
class PartyFrozen(capkpi.ValidationError):
	pass


class InvalidAccountCurrency(capkpi.ValidationError):
	pass


class InvalidCurrency(capkpi.ValidationError):
	pass


class PartyDisabled(capkpi.ValidationError):
	pass


class InvalidAccountDimensionError(capkpi.ValidationError):
	pass


class MandatoryAccountDimensionError(capkpi.ValidationError):
	pass
