# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PracticeProblemSubmission(Document):
    def before_save(self):
        pass

    def after_insert(self):
        q = {
            "training": self.training,
            "author": self.author,
            "problem_set": self.problem_set,
            "problem": self.problem
        }
        names = frappe.get_all("Practice Problem Latest Submission", filters=q)
        if names:
            latest = frappe.get_doc("Practice Problem Latest Submission", names[0])
            latest.code = self.code
            latest.latest_submission = self.name
            latest.save(ignore_permissions=True)
        else:
            data = dict(q, doctype="Practice Problem Latest Submission", latest_submission=self.name, code=self.code)
            latest = frappe.get_doc(data)
            latest.insert(ignore_permissions=True)
