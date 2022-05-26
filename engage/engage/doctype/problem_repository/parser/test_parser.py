from pathlib import Path
from unittest import TestCase

from . import ProblemValidationError, parse_config


class TestParserConfig(TestCase):
    def setUp(self):
        self.ok_config_file = Path(__file__).parent / "data" / "1_ok_problem.yml"
        self.parsed_ok_config_file = {
            "title": "n-th Fibonacci number",
            "blurb": "For the fibonacci series starting with 0 and 1, calculate the n-th fibonacci number",
            "files": {
                "code": ["fib.py"],
                "test": ["test_fib.py"],
                "data": ["input.txt"],
                "solution": ["solution/fib.py"],
            }
        }

        self.missing_title_config_file = Path(__file__).parent / "data" / "2_missing_title_problem.yml"

        self.missing_code_files_config_file = Path(__file__).parent / "data" / "3_missing_code_files_problem.yml"

    def test_parse_config_ok(self):
        conf = parse_config(self.ok_config_file)

        self.assertEqual(conf, self.parsed_ok_config_file)

    def test_parse_config_when_title_is_missing(self):
        with self.assertRaises(ProblemValidationError):
            parse_config(self.missing_title_config_file)

    def test_parse_config_when_code_files_are_missing(self):
        with self.assertRaises(ProblemValidationError):
            parse_config(self.missing_code_files_config_file)
