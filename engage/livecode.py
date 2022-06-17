"""
engage.livecode
~~~~~~~~~~~~~~~

API endpoints for livecode integration.
"""

import frappe
import requests

def get_livecode_url():
    return "https://livecode.pipal.in"

@frappe.whitelist(allow_guest=True)
def execute(problem, code):
    """Runs the code for given problem.

    The response format will be like:

        >>> execute("python/hello", "print('hello')")
        {"ok":true,"output":"hello\n"}

    When called via an API, the return value will be wrapped as follows.

        {"message":{"ok":true,"output":"hello\n"}}
    """
    runner = ProblemRunner(problem)
    return runner.execute(code)

@frappe.whitelist(allow_guest=True)
def run_tests(problem, code):
    """Runs the tests for a problem with given code.

    Sample return format:

        >>> runtests("python/digit_count", "def digit_count(num, d): return str(num).count(str(d))")
        {
          "outcome":"passed",
          "testcases":[
            {"filename":"test_digit_count.py","name":"test_function_name","time_taken":"0.002","outcome":"passed"},
            {"filename":"test_digit_count.py","name":"test_examples","time_taken":"0.001","outcome":"passed"}
          ],
          "stats":{
            "tests":"2",
            "passed":2,
            "failed":0,
            "time_taken":"0.072"
          }
        }
    """
    runner = ProblemRunner(problem)
    return runner.run_tests(code)

class ProblemRunner:
    def __init__(self, problem_name):
        self.problem = frappe.get_doc("Practice Problem", problem_name)
        self.source_file = self.problem.code_files[0].relative_path

    def prepare_headers(self, mode):
        source_file = self.source_file
        return {
            "x-falcon-mode": mode,
            "x-falcon-env": f"FALCON_SOURCE_FILE={source_file}"
        }

    def prepare_files(self, code, mode):
        files = {}
        def add_file(filename, contents):
            files[filename] = (filename, contents)

        add_file(self.source_file, code)
        for f in self.problem.data_files:
            add_file(f.relative_path, f.content)

        if mode == "test":
            for f in self.problem.test_files:
                add_file(f.relative_path, f.content)

        return files

    def post(self, files, headers):
        runtime = "python"
        base_url = get_livecode_url()
        url = f"{base_url}/runtimes/{runtime}"
        return requests.post(url, files=files, headers=headers)

    def run_tests(self, code):
        headers = self.prepare_headers(mode="test")
        files = self.prepare_files(code, mode="test")
        res = self.post(files=files, headers=headers)

        if res.status_code != 200:
            return {
                "ok": False,
                "error": f"Exection failed with status code {res.status_code}",
                "message": res.text
            }
        else:
            return dict(res.json(), ok=True)

    def execute(self, code):
        headers = self.prepare_headers(mode="exec")
        files = self.prepare_files(code, mode="exec")

        res = self.post(files=files, headers=headers)
        if res.status_code != 200:
            return {
                "ok": False,
                "error": f"Exection failed with status code {res.status_code}",
                "message": res.text
            }
        else:
            return {"ok": True, "output": res.text}
