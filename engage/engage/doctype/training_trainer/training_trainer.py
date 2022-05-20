# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingTrainer(Document):
	pass


def on_doctype_update():
    frappe.db.add_unique("Training Trainer", ["parent", "user"])
