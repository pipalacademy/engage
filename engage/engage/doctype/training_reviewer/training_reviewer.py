# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingReviewer(Document):
	pass


def on_doctype_update():
     # only one reviewer should be added once per training
     frappe.db.add_unique("Training Reviewer", ["parent", "user"])
