# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ProblemSet(Document):
    def autoname(self):
        self.name = self.title.lower().replace(" ", "-")
