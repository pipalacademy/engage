import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from .custom_types import PathString


class NotAProblemDirectoryError(Exception):
    pass


class ProblemValidationError(Exception):
    pass


class FileDoesNotExistError(Exception):
    pass


class ParsedFile(NamedTuple):
    """
    Class to keep parsed problem files.

    Have 2 data attributes:
    1. content - content of file as a str
    2. relative_path - path of the file relative to the problem directory base as a str.
        This should be the path that was mentioned in problem.yml
    """
    content: str
    relative_path: str


class ParsedProblem:

    def __init__(self,
                 base_path: PathString,
                 title: str,
                 blurb: str,
                 files: Dict[str, List[PathString]],
                 slug: Optional[str] = None,
                 description: Optional[str] = None,
                 description_file: Optional[str] = None,
                 source: Optional[str] = None,
                 source_url: Optional[str] = None):

        self.base_path = Path(base_path)  # path to problem's base dir

        self.slug = slug or self.base_path.name
        self.title = title
        self.blurb = blurb

        self.description_file = self.base_path / (description_file
                                                  or "description.md")
        self.description = description or parse_description_file(
            self.description_file,
            default=get_default_description(self.title, self.blurb))

        # defaults
        self.files: Dict[str, List[ParsedFile]] = {
            "code": [],
            "data": [],
            "test": [],
            "solution": [],
        }

        for kind in self.files:
            if kind in files:
                self.files[kind] = [
                    parse_problem_file(self.base_path, os.fspath(fpath))
                    for fpath in files[kind]
                ]

        self.source = source
        self.source_url = source_url


def parse_problem_repository(
        parent_directory: PathString) -> List[ParsedProblem]:
    """
    Gets all the problems from a problem repository
    """
    parent_directory = Path(parent_directory)

    problems = []

    for child in parent_directory.iterdir():
        if not child.is_dir():
            continue

        try:
            problem = parse_problem_directory(child)
        except NotAProblemDirectoryError:
            pass
        else:
            problems.append(problem)

    return problems


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


def parse_problem_file(problem_directory: PathString,
                       relative_filepath: str) -> ParsedFile:
    """
    problem_directory: base path to problem directory (on disk)
    relative_filepath: path to the problem file (as a str), relative to `probdir_path`. This is the path
        set by trainer in problem.yml
    """
    with open(Path(problem_directory) / relative_filepath) as f:
        return ParsedFile(content=f.read(), relative_path=relative_filepath)


def parse_description_file(description_file: Path, default: str) -> str:
    if not description_file.exists():
        return default

    with open(description_file) as f:
        return f.read()


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
        if not (problem.base_path / f.relative_path).exists():
            raise FileDoesNotExistError(
                f"file {f} does not exist (referenced in files->{key})")


def get_default_description(title: str, blurb: str) -> str:
    return f"# {title}\n\n{blurb}\n"
