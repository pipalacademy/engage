from os import PathLike
from pathlib import Path
from typing import List, Optional

import git

from .typing_fun import SingleOrList


class ParsedProblem:
    def __init__(
            self,
            base_path: PathLike,
            commit_version: str,
            title: str,
            blurb: str,
            code: SingleOrList[PathLike],
            test: SingleOrList[PathLike],
            files: List[PathLike],
            slug: Optional[str] = None,
            solution: Optional[PathLike] = None,
            description: Optional[PathLike] = None):

        self.base_path = Path(path)  # path to problem's base dir
        self.commit_version = commit_version
        self.title = title
        self.blurb = blurb
        self.code = [self.base_path / Path(f_path) for f_path in code]
        self.files = [self.base_path / Path(f_path) for f_path in files]
        self.test = [self.base_path / Path(f_path) for f_path in test]

        self.slug = slug or self.base_path.name
        self.solution = self.base_path / (solution or "solution/")
        self.description = self.base_path / (description or "description.md")


def shallow_clone(git_url: str, dir_path: PathLike) -> git.Repo:
    repo = git.Repo.clone_from(git_url, dir_path, depth=1)
    return repo


def get_github_repo_url(owner: str, name: str, token: Optional[str] = None) -> str:
    base_host = "github.com"
    if token:
        base_host = f"{token}@{base_host}"

    return f"https://{base_host}/{owner}/{name}"
