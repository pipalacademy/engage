# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProblemSetReference(Document):

    def refresh_status(self):
        """
        Refreshes status depending on the publish_time and deadline.
        Returns True if the status was changed
        """
        nowtime = frappe.utils.now_datetime()
        modified = False

        if (self.publish_time and not self.is_published
                and nowtime >= self.publish_time):
            self.status = "Published"
            modified = True

        if (self.deadline and self.is_published
                and nowtime >= self.deadline):
            self.status = "Closed"
            modified = True

        return modified

    @property
    def is_published(self):
        return self.status in {"Published", "Closed"}
