# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.model.document import Document


class TrainingParticipantsChildTable(Document):
    pass


def on_doctype_update():
    # a user can only register once per training (parent is training)
    frappe.db.add_unique("Training Participants Child Table", fields=["parent", "user"])
