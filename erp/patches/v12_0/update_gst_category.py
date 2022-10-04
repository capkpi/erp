import capkpi


def execute():

	company = capkpi.get_all("Company", filters={"country": "India"})
	if not company:
		return

	capkpi.db.sql(
		""" UPDATE `tabSales Invoice` set gst_category = 'Unregistered'
        where gst_category = 'Registered Regular'
        and ifnull(customer_gstin, '')=''
        and ifnull(billing_address_gstin,'')=''
    """
	)

	capkpi.db.sql(
		""" UPDATE `tabPurchase Invoice` set gst_category = 'Unregistered'
        where gst_category = 'Registered Regular'
        and ifnull(supplier_gstin, '')=''
    """
	)
