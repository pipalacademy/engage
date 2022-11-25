# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import requests

JUPYTERHUB_DASHBOARD_ENDPOINT = "/services/dashboard"


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

    def refresh_problem_sets(self):
        """
        Refreshes status of problem sets.
        Returns True if any of the problem sets was changed
        """
        modified = False
        for pset in self.problem_sets:
            modified = modified or pset.refresh_status()

        return modified

    def add_participant(self, user, send_invitation_mail=False):
        """
        Adds a user as a participant to the training
        """
        if user.name in self.get_participant_usernames():
            return False

        self.append("participants", {"user": user.name})
        if send_invitation_mail:
            frappe.sendmail(
                recipients=[user.name],
                subject="[Engage] Invitation to join training",
                template="training_invitation",
                args={
                    "training": self,
                    "invitee": user,
                    "inviter": frappe.get_doc("User", frappe.session.user),
                    "training_url": self.url,
                },
                with_container=True,
                delayed=False)

        return True

    def get_participant_usernames(self):
        return [p.user for p in self.participants]

    def before_save(self):
        # self._add_trainers_as_participants()
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

    def create_jupyterhub_user(self, jh_username, jh_password):
        if not self.jupyterhub_url:
            raise Exception("JupyterHub URL is not set")
        if not self.jupyterhub_token:
            raise Exception("JupyterHub Token is not set")

        url = self.jupyterhub_url + JUPYTERHUB_DASHBOARD_ENDPOINT + "/users"
        headers = {"Authorization": f"token {self.jupyterhub_token}"}
        r = requests.post(url, headers=headers,
                          json={"username": jh_username, "password": jh_password})
        return r

    @property
    def url(self):
        return frappe.utils.get_url(f"/trainings/{self.name}/")


@frappe.whitelist()
def create_jupyterhub_user(training_name, participant_name, jh_username, jh_password):
    training = frappe.get_doc("Training", training_name)
    participant = next(p for p in training.participants if p.name == participant_name)
    response = training.create_jupyterhub_user(jh_username=jh_username, jh_password=jh_password)
    if response.ok:
        participant.jh_username = jh_username
        participant.jh_password = jh_password
        participant.save()
    elif "json" in response.headers["content-type"]:
        frappe.response.update(response.json())
    else:
        frappe.response["message"] = f"{response.status_code} {response.reason}"

    frappe.response["ok"] = response.ok


def slugify(s):
    return s.lower().replace(" ", "-")
