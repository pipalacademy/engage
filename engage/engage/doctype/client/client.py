# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Client(Document):
    def autoname(self):
        self.name = self.slug

    def before_insert(self):
        if not self.slug:
            self.slug = self.title.lower().replace(" ", "-")
