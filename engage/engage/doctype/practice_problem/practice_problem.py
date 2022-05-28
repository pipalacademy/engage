# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PracticeProblem(Document):
    def autoname(self):
        if self.problem_repository:
            self.name = f"{self.problem_repository}/{self.slug}"
        else:
            self.name = self.slug

    def get_problem_files_by_kind(self, kind):
        return [f for f in self.problem_files if f.kind == kind]

    @property
    def code_files(self):
        return self.get_problem_files_by_kind("code")

    @property
    def data_files(self):
        return self.get_problem_files_by_kind("data")

    @property
    def test_files(self):
        return self.get_problem_files_by_kind("test")

    @property
    def solution_files(self):
        return self.get_problem_files_by_kind("solution")
