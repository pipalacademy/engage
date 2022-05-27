# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PracticeProblem(Document):
    def autoname(self):
        if self.problem_repository:
            self.name = f"{self.problem_repository}/{self.slug}"
        else:
            self.name = self.slug
