# Copyright (c) 2018, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import capkpi
from capkpi import _
from capkpi.model.document import Document


class Quiz(Document):
	def validate(self):
		if self.passing_score > 100:
			capkpi.throw(_("Passing Score value should be between 0 and 100"))

	def allowed_attempt(self, enrollment, quiz_name):
		if self.max_attempts == 0:
			return True

		try:
			if (
				len(capkpi.get_all("Quiz Activity", {"enrollment": enrollment.name, "quiz": quiz_name}))
				>= self.max_attempts
			):
				capkpi.msgprint(_("Maximum attempts for this quiz reached!"))
				return False
			else:
				return True
		except Exception as e:
			return False

	def evaluate(self, response_dict, quiz_name):
		questions = [capkpi.get_doc("Question", question.question_link) for question in self.question]
		answers = {q.name: q.get_answer() for q in questions}
		result = {}
		for key in answers:
			try:
				if isinstance(response_dict[key], list):
					is_correct = compare_list_elementwise(response_dict[key], answers[key])
				else:
					is_correct = response_dict[key] == answers[key]
			except Exception as e:
				is_correct = False
			result[key] = is_correct
		score = (sum(result.values()) * 100) / len(answers)
		if score >= self.passing_score:
			status = "Pass"
		else:
			status = "Fail"
		return result, score, status

	def get_questions(self):
		return [capkpi.get_doc("Question", question.question_link) for question in self.question]


def compare_list_elementwise(*args):
	try:
		if all(len(args[0]) == len(_arg) for _arg in args[1:]):
			return all(all([element in (item) for element in args[0]]) for item in args[1:])
		else:
			return False
	except TypeError:
		capkpi.throw(_("Compare List function takes on list arguments"))


@capkpi.whitelist()
def get_topics_without_quiz(quiz):
	data = []
	for entry in capkpi.db.get_all("Topic"):
		topic = capkpi.get_doc("Topic", entry.name)
		topic_contents = [tc.content for tc in topic.topic_content]
		if not topic_contents or quiz not in topic_contents:
			data.append(topic.name)
	return data
