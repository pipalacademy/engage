from pathlib import Path
from unittest import TestCase

from . import NotAProblemDirectoryError, ProblemValidationError, parse_config, parse_problem_directory


TEST_DATA_BASE = Path(__file__).parent / "data"
TEST_PROB_DIRS_BASE = TEST_DATA_BASE / "problem_directories"


class TestParseConfig(TestCase):
    def setUp(self):
        self.ok_config_file = TEST_DATA_BASE / "1_ok_problem.yml"
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

        self.missing_title_config_file = TEST_DATA_BASE / "2_missing_title_problem.yml"

        self.missing_code_files_config_file = TEST_DATA_BASE / "3_missing_code_files_problem.yml"

    def test_parse_config_ok(self):
        conf = parse_config(self.ok_config_file)

        self.assertEqual(conf, self.parsed_ok_config_file)

    def test_parse_config_when_title_is_missing(self):
        with self.assertRaises(ProblemValidationError):
            parse_config(self.missing_title_config_file)

    def test_parse_config_when_code_files_are_missing(self):
        with self.assertRaises(ProblemValidationError):
            parse_config(self.missing_code_files_config_file)


class TestParseProblemDirectory(TestCase):
    def setUp(self):
        self.ok_problem_directory = TEST_PROB_DIRS_BASE / "fibonacci"
        self.normal_directory = TEST_PROB_DIRS_BASE / "not-a-problem-directory"

    def test_ok_parse_problem_directory(self):
        problem = parse_problem_directory(self.ok_problem_directory)

        base_path = self.ok_problem_directory

        self.assertEqual(problem.base_path, base_path)
        self.assertEqual(problem.slug, "fibonacci")
        self.assertEqual(problem.title, "n-th Fibonacci number")
        self.assertEqual(problem.blurb, "For the fibonacci series starting with 0 and 1, calculate the n-th fibonacci number")

        expected_code_files = [base_path / "fib.py"]
        expected_data_files = []
        expected_test_files = [base_path / "test_fib.py"]
        expected_solution_files = [base_path / "solution" / "fib.py"]

        self.assertListEqual(problem.files["code"], expected_code_files)
        self.assertListEqual(problem.files["data"], expected_data_files)
        self.assertListEqual(problem.files["test"], expected_test_files)
        self.assertListEqual(problem.files["solution"], expected_solution_files)

        self.assertIsNone(problem.source)
        self.assertIsNone(problem.source_url)

    def test_dir_which_is_not_a_problem_directory(self):
        with self.assertRaises(NotAProblemDirectoryError):
            parse_problem_directory(self.normal_directory)
