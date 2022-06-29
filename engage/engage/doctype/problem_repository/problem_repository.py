# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import hashlib
import json
import string
import tempfile
from pathlib import Path

import requests

import frappe
from frappe.model.document import Document

from .parser import parse_problem_repository
from .util import get_commit_hash, get_default_branch, get_github_repo_url, get_latest_commit, shallow_clone, flatten_to_tuples


class ProblemRepository(Document):

    def autoname(self):
        # slugify title
        self.name = self.title.lower().replace(" ", "-")

    def validate(self):
        if not is_github_username_valid(self.github_repo_owner):
            raise frappe.exceptions.ValidationError(
                "Repo owner username is not valid")

        if not is_github_repo_name_valid(self.github_repo_name):
            raise frappe.exceptions.ValidationError("Repo name is not valid")

    def before_insert(self):
        # set branch to default github branch
        if not self.branch:
            self.branch = get_default_branch(self.github_repo_owner,
                                             self.github_repo_name,
                                             self.github_token)

    def does_repo_exist(self):
        url = "https://api.github.com/repos/{self.github_repo_owner}/{self.github_repo_name}"

        r = requests.get(url)
        return r.ok

    def clone(self, to_path):
        """
        `git clone` repository to a local path (as given by path)
        
        Note: Performs a shallow clone only
        """
        clone_url = get_github_repo_url(self.github_repo_owner,
                                        self.github_repo_name,
                                        token=self.github_token)
        return shallow_clone(clone_url, to_path, branch=self.branch)

    def update_problems(self):
        with tempfile.TemporaryDirectory() as tempdir:
            repo = self.clone(tempdir)
            commit_hash = get_commit_hash(repo)

            problems_base_dir = Path(tempdir) / (self.parent_directory or "")
            problems = parse_problem_repository(problems_base_dir)

        # counter to confirm how many problems were written
        counter = 0

        # create problems for the repository
        for parsed_problem in problems:
            _, updated = self.update_or_create_child_problem(parsed_problem)
            counter += updated

        if commit_hash != self.commit_hash:
            self.commit_hash = commit_hash
            self.save()

        return counter

    def update_or_create_child_problem(self, parsed_problem):
        problem = get_problem(self.name, parsed_problem.slug)
        has_changed = problem.is_new() or False

        def update_problem(attr, new_value):
            nonlocal has_changed
            if getattr(problem, attr) != new_value:
                setattr(problem, attr, new_value)
                has_changed = True

        update_problem("title", parsed_problem.title)
        update_problem("blurb", parsed_problem.blurb)
        update_problem("description", parsed_problem.description)

        update_problem("source", parsed_problem.source)
        update_problem("source_url", parsed_problem.source_url)

        old_files = [
            serialize_file(f.kind, f.relative_path, f.content)
            for f in problem.files
        ]
        new_files = [
            serialize_file(kind, f.relative_path, f.content)
            for (kind, f) in flatten_to_tuples(parsed_problem.files)
        ]

        # if any file has changed, remove all files and re-add them
        files_changed = have_files_changed(old_files, new_files)

        if not problem.is_new() and files_changed:
            frappe.db.delete("Problem File",
                             filters={
                                 "parenttype": "Practice Problem",
                                 "parent": problem.name,
                             })
            update_problem("files", [])

        if problem.is_new() or files_changed:
            for pfile in new_files:
                problem.append("files", pfile)
            has_changed = True

        if has_changed:
            problem.save()

        return problem, has_changed

    def is_new(self):
        return not self.name

    @frappe.whitelist()
    def is_update_available(self):
        last_commit = get_latest_commit(self.github_repo_owner,
                                        self.github_repo_name,
                                        self.branch,
                                        token=self.github_token)
        if last_commit != self.commit_hash:
            return last_commit


@frappe.whitelist()
def update_problems(problem_repository_name):
    doc = frappe.get_doc("Problem Repository", problem_repository_name)
    count = doc.update_problems()
    frappe.response["count"] = count
    return count


@frappe.whitelist()
def update_problems_as_action(args):
    problem_repository_name = json.loads(args)["problem_repository_name"]
    return update_problems(problem_repository_name)


@frappe.whitelist()
def check_for_updates(problem_repository_name):
    doc = frappe.get_doc("Problem Repository", problem_repository_name)
    if (latest_commit := doc.is_update_available()):
        frappe.response["available"] = True
        frappe.response["latest_commit"] = latest_commit
    else:
        frappe.response["available"] = False


def have_files_changed(old, new):
    if len(old) != len(new): return True

    old_hashes = {hash_serialized_file(f) for f in old}
    new_hashes = {hash_serialized_file(f) for f in new}

    return old_hashes != new_hashes


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


def hash_together(*args):
    h = hashlib.blake2s()
    for item in args:
        h.update(item.encode())

    return h.hexdigest()


def get_problem(repo_name, slug):
    problem_id = f"{repo_name}/{slug}"

    if frappe.db.exists("Practice Problem", problem_id):
        return frappe.get_doc("Practice Problem", problem_id)

    return frappe.get_doc({
        "doctype": "Practice Problem",
        "slug": slug,
        "problem_repository": repo_name,
    })


def serialize_file(kind, relative_path, content):
    return {"kind": kind, "relative_path": relative_path, "content": content}


def hash_serialized_file(f):
    return hash_together(f["kind"], f["relative_path"], f["content"])
