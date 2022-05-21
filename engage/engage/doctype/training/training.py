# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Training(Document):
    def autoname(self):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + slugify(self.client)

        self.name = f"{self.year}/{self.slug}"


def slugify(s):
    return s.lower().replace(" ", "-")
