# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi.model.document import Document


class WebsiteOffer(Document):
	pass


@capkpi.whitelist(allow_guest=True)
def get_offer_details(offer_id):
	return capkpi.db.get_value("Website Offer", {"name": offer_id}, ["offer_details"])
