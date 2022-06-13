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

        return any(filter(lambda t: t.user == user, self.trainers))

    def has_user_as_participant(self, user):
        """Returns a boolean for whether the given user is a participant for this training or not
        """
        if not isinstance(user, str):
            user = user.name

        return any(filter(lambda p: p.user == user, self.participants))

    def before_save(self):
        # add trainers as participants, so that they get JupyterHub credentials and
        # access to web pages that students can access
        for t in self.trainers:
            if not self.has_user_as_participant(t.user):
                self.append("participants", {
                    "user": t.user,
                })


def slugify(s):
    return s.lower().replace(" ", "-")
