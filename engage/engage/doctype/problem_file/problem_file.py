# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import hashlib

# import frappe
from frappe.model.document import Document


class ProblemFile(Document):
    def autoname(self):
        self.name = compute_problem_file_name(self.parent, self.kind, self.relative_path)


def compute_problem_file_name(problem_id, kind, relative_path):
    return hash_together(problem_id, kind, relative_path)[:10]


def hash_together(*args):
    combination = "\x1f".join(args)
    return hashlib.md5(bytes(combination, encoding="utf-8")).hexdigest()
