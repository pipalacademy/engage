# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

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
            raise frappe.exceptions.ValidationError("Repo owner username is not valid")

        if not is_github_repo_name_valid(self.github_repo_name):
            raise frappe.exceptions.ValidationError("Repo name is not valid")

    def before_insert(self):
        # set branch to default github branch
        if not self.branch:
            self.branch = get_default_branch(self.github_repo_owner, self.github_repo_name, self.github_token)

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
            self.update_or_create_child_problem(parsed_problem, commit_hash)
            counter += 1

        self.commit_hash = commit_hash
        self.save()

        return counter

    def update_or_create_child_problem(self, parsed_problem, commit_hash):
        problem_id = f"{self.name}/{parsed_problem.slug}"

        if frappe.db.exists("Practice Problem", problem_id):
            problem = frappe.get_doc("Practice Problem", problem_id)
        else:
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
            f.delete()

        problem.reload()

        for (kind, pfile) in flatten_to_tuples(parsed_problem.files):
            problem.append("files", {
                "kind": kind,
                "relative_path": pfile.relative_path,
                "content": pfile.content,
            })

        problem.save()
        return problem

    @frappe.whitelist()
    def is_update_available(self):
        last_commit = get_latest_commit(
                self.github_repo_owner,
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
