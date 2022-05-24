# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Training(Document):
    def autoname(self):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + self.client

        self.name = f"{self.year}/{self.slug}"

    def has_user_as_trainer(self, user):
        """Returns a boolean for whether the given user is a trainer for this training or not
        """
        if not isinstance(user, str):
            user = user.name

        return bool(filter(lambda t: t.user == user, self.trainers))


def slugify(s):
    return s.lower().replace(" ", "-")
