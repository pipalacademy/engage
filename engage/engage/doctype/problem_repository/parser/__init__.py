import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

import git

from .types import SingleOrList, PathString


class NotAProblemDirectoryError(Exception):
    pass


class ProblemValidationError(Exception):
    pass


class FileDoesNotExistError(Exception):
    pass


class ParsedProblem:

    def __init__(self,
                 base_path: PathString,
                 title: str,
                 blurb: str,
                 files: Dict[str, SingleOrList[PathString]],
                 slug: Optional[str] = None,
                 description_file: Optional[str] = "description.md",
                 source: Optional[str] = None,
                 source_url: Optional[str] = None):

        self.base_path = Path(base_path)  # path to problem's base dir

        self.slug = slug or self.base_path.name
        self.title = title
        self.blurb = blurb
        self.description_file = self.base_path / description_file

        # defaults
        self.files = {
            "code": [],
            "data": [],
            "test": [],
            "solution": [],
        }

        # convert PathLike/string to pathlib.Path
        for key in self.files:
            if key in files:
                self.files[key] += list(
                    map(lambda f_path: self.base_path / f_path, files[key]))

        self.source = source
        self.source_url = source_url


def parse_problem_directory(fs_path: Path) -> ParsedProblem:
    if not (fs_path / "problem.yml").exists():
        raise NotAProblemDirectoryError("problem.yml not found")

    config = parse_config(fs_path / "problem.yml")

    problem = ParsedProblem(
        fs_path,
        **config,
    )

    validate_files_list(problem, "code")
    validate_files_list(problem, "data")
    validate_files_list(problem, "test")
    validate_files_list(problem, "solution")

    return problem


def parse_config(problem_yml: Path) -> Dict[str, Any]:
    """
    Parse the problem.yml config file.

    This is the schema for the file:
    ```
    slug: optional[str]
    title: str
    blurb: str
    description_file: optional[path-string]

    files: map[str -> list[path-string]], allowed keys :-
        code: list[path-string] (required!)
        test: list[path-string] (required!)
        data: list[path-string] (optional)
        solution: list[path-string] (optional)

    source: optional[str]
    source_url: optional[str]
    ```

    An example file could be:
    ```yaml
    title: n-th Fibonacci number
    blurb: For the fibonacci series starting with 0 and 1, calculate the n-th fibonacci number

    files:
        code:
            - fib.py
        test:
            - test_fib.py
        data:
            - input.txt
        solution: 
            - solution/fib.py
    ```
    """
    with open(problem_yml) as f:
        config = yaml.safe_load(f)

    validate_config(config)

    return config


def validate_config(config: Dict[Any, Any]):
    # TODO: investigate using cerberus or a more robust solution for testing.
    # for now, some cases are missed. like, type-validation for optionals

    # some simple by-hand validation
    validate_required(config, "title")
    validate_required(config, "blurb")
    validate_required(config, "files")

    validate_type(config, "title", str)
    validate_type(config, "blurb", str)
    validate_type(config, "files", dict)

    validate_required(config["files"], "code", err_prefix="problem.yml->files")
    validate_required(config["files"], "test", err_prefix="problem.yml->files")

    validate_list_str(config["files"], "code", err_prefix="problem.yml->files")
    validate_list_str(config["files"], "test", err_prefix="problem.yml->files")


def validate_required(obj: Dict[Any, Any],
                      key: Any,
                      err_prefix: str = "problem.yml"):
    if key not in obj:
        raise ProblemValidationError(f"{err_prefix}: {key} is required")


def validate_type(obj: Dict[Any, Any],
                  key: Any,
                  expected_type: type,
                  err_prefix: str = "problem.yml"):
    if not isinstance(obj[key], expected_type):
        raise ProblemValidationError(
            f"{err_prefix}: {key} should be of type {expected_type}")


def validate_list_str(obj: Dict[Any, Any],
                      key: Any,
                      err_prefix: str = "problem.yml"):
    """Validate that given key is a list of strings
    """
    validate_type(obj, key, list, err_prefix=err_prefix)

    for item in obj[key]:
        if not isinstance(item, str):
            raise ProblemValidationError(
                f"{err_prefix}: {key} should be of type list[str]")


def validate_files_list(problem: ParsedProblem, key: str):
    files = problem.files[key]

    for f in files:
        if not f.exists():
            raise ReferencedFileDoesNotExistError(f"file {f} does not exist (referenced in files->{key})")
