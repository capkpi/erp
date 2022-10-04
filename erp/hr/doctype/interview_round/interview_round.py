# Copyright (c) 2021, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
from capkpi.model.document import Document


class InterviewRound(Document):
	pass


@capkpi.whitelist()
def create_interview(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = capkpi.get_doc(doc)

	interview = capkpi.new_doc("Interview")
	interview.interview_round = doc.name
	interview.designation = doc.designation

	if doc.interviewers:
		interview.interview_details = []
		for data in doc.interviewers:
			interview.append("interview_details", {"interviewer": data.user})
	return interview
