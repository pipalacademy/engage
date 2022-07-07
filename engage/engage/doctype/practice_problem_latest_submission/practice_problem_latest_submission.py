# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PracticeProblemLatestSubmission(Document):

    def before_save(self):
        old_doc = self.get_doc_before_save()
        if not old_doc or old_doc.latest_submission != self.latest_submission:
            self.for_review = True

    def after_review(self):
        self.for_review = 0
        self.save(ignore_permissions=True)
        self.reload()


def on_new_comment(doc, event_name):
    topic = frappe.get_doc("Discussion Topic", doc.topic)
    if topic.reference_doctype == "Practice Problem Latest Submission":
        submission = frappe.get_doc("Practice Problem Latest Submission",
                                    topic.reference_docname)
        training = frappe.get_doc("Training", submission.training)

        if training.has_user_as_trainer(doc.owner):
            # reviewed by trainer
            submission.after_review()
