# Copyright (c) 2022, Pipal Academy and Contributors
# See license.txt

import tempfile
from unittest import TestCase

import git

import frappe
from frappe.tests.utils import FrappeTestCase


class TestProblemRepository(FrappeTestCase):
    def setUp(self):
        self.problem_repository = frappe.get_doc({
            "doctype": "Problem Repository",
            "github_repo_owner": "pipalacademy",
            "github_repo_name": "pipal.in",
        })
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempdir_path = self.tempdir.name

    def tearDown(self):
        self.tempdir.cleanup()

    def test_clone_repo_ok(self):
        self.problem_repository.clone(self.tempdir_path)
        self.assertFalse(git.Repo(self.tempdir_path).bare)

    def test_sync_problems_ok(self):
        pass
