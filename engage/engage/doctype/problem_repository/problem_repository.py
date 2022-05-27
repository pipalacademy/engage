# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import string
import tempfile
from pathlib import Path

import requests

import frappe
from frappe.model.document import Document

from .parser import parse_problem_repository
from .util import get_commit_hash, get_github_repo_url, shallow_clone, flatten_to_tuples


class ProblemRepository(Document):
    def autoname(self):
        # slugify title
        self.name = self.title.lower().replace(" ", "-")

    def validate(self):
        if not is_github_username_valid(self.github_repo_owner):
            raise frappe.exceptions.ValidationError("Repo owner username is not valid")

        if not is_github_repo_name_valid(self.github_repo_name):
            raise frappe.exceptions.ValidationError("Repo name is not valid")

    def does_repo_exist(self):
        url = "https://api.github.com/repos/{self.github_repo_owner}/{self.github_repo_name}"

        r = requests.get(gh_api_url)
        return r.ok

    def clone(self, to_path):
        """
        `git clone` repository to a local path (as given by path)
        
        Note: Performs a shallow clone only
        """
        clone_url = get_github_repo_url(self.github_repo_owner, self.github_repo_name, token=self.github_token)
        return shallow_clone(clone_url, to_path)

    def sync_problems(self):
        with tempfile.TemporaryDirectory() as tempdir:
            repo = self.clone(tempdir)
            commit_hash = get_commit_hash(repo)

            problems_base_dir = Path(tempdir) / (self.parent_directory or "")
            problems = parse_problem_repository(problems_base_dir)

        # counter to confirm how many problems were written
        counter = 0

        # create problems for the repository
        for parsed_problem in problems:
            self.update_or_create_child_problem(parsed_problem, commit_hash)
            counter += 1

        self.commit_hash = commit_hash
        self.save()

        return counter


    def update_or_create_child_problem(self, parsed_problem, commit_hash):
        problem_id = f"{self.name}/{parsed_problem.slug}"

        try:
            problem = frappe.get_doc("Practice Problem", problem_id)
        except frappe.exceptions.DoesNotExistError:
            problem = frappe.get_doc({
                "doctype": "Practice Problem",
                "slug": parsed_problem.slug,
                "problem_repository": self.name,
            })

        problem.title = parsed_problem.title
        problem.blurb = parsed_problem.blurb
        problem.description = parsed_problem.description

        problem.source = parsed_problem.source
        problem.source_url = parsed_problem.source_url

        problem.commit_hash = commit_hash
        problem.save()

        # empty problem.files to re-add the files
        for f in problem.files:
            frappe.delete_doc("Problem File", f.name)

        problem.reload()

        for (kind, pfile) in flatten_to_tuples(parsed_problem.files):
            problem.append("files", {
                "kind": kind,
                "relative_path": pfile.relative_path,
                "content": pfile.content,
            })

        problem.save()
        return problem


def is_github_username_valid(val):
    max_length = 39
    allowed_chars = string.ascii_letters + string.digits + "-"

    if len(val) > max_length:
        return False

    for char in val:
        if char not in allowed_chars:
            return False

    return True


def is_github_repo_name_valid(val):
    max_length = 100
    allowed_chars = string.ascii_letters + string.digits + "-_."

    if len(val) > max_length:
        return False

    for char in val:
        if char not in allowed_chars:
            return False

    return True


def get_first_or_init(doctype, filters, defaults):
    doc = frappe.get_first_doc(filters)
    if not doc:
        doc = frappe.get_doc({"doctype": doctype, **defaults})

    return doc
