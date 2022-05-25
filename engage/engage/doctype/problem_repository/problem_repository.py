# Copyright (c) 2022, Pipal Academy and contributors
# For license information, please see license.txt

import string
import tempfile

import requests

# import frappe
from frappe.model.document import Document

from git_util import get_github_repo_url, shallow_clone


class ProblemRepository(Document):
    def autoname(self):
        # slugify title
        self.name = title.lower().replace(" ", "-")

    def validate(self):
        if not is_github_username_valid(self.github_repo_owner):
            raise frappe.exceptions.ValidationError("Repo owner username is not valid")

        if not is_github_repo_name_valid(self.github_repo_name):
            raise frappe.exceptions.ValidationError("Repo name is not valid")

    def does_repo_exist(self):
        url = "https://api.github.com/repos/{self.github_repo_owner}/{self.github_repo_name}"

        r = requests.get(gh_api_url)
        return r.ok

    def clone(self, to_path: "os.PathLike"):
        """
        `git clone` repository to a local path (as given by path)
        
        Note: Performs a shallow clone only
        """
        clone_url = get_github_repo_url(self.github_repo_owner, self.github_repo_name)
        return shallow_clone(clone_url, to_path)


def is_github_val_valid(val):
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
