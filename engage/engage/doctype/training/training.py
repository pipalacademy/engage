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
        self._add_trainers_as_participants()
        self._set_slug_on_problem_sets()

    def _add_trainers_as_participants(self):
        # add trainers as participants, so that they get JupyterHub credentials and
        # access to web pages that students can access
        for t in self.trainers:
            if not self.has_user_as_participant(t.user):
                self.append("participants", {
                    "user": t.user,
                })

    def _set_slug_on_problem_sets(self):
        """
        Routing depends on the slugs set to problem set references. If it is not set,
        the problems page won't be reached
        """
        for pset_ref in self.problem_sets:
            if not pset_ref.slug:
                pset_ref.slug = slugify(pset_ref.title)


def slugify(s):
    return s.lower().replace(" ", "-")

