from pathlib import Path
from typing import List, Optional

import git

from .typing_fun import SingleOrList, PathString


class ParsedProblem:
    def __init__(
            self,
            base_path: PathString,
            commit_version: str,
            title: str,
            blurb: str,
            files: Dict[str, SingleOrList[PathString]],
            slug: Optional[str] = None,
            description_file: Optional[str] = "description.md"):

        self.base_path = Path(path)  # path to problem's base dir
        self.commit_version = commit_version

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

        # update from args
        self.files.update(files)

        # convert PathLike to pathlib.Path
        for key in ["code", "data", "test", "solution"]:
            self.files[key] = [self.base_path / Path(f_path) for f_path in code]


def shallow_clone(git_url: str, dir_path: PathLike) -> git.Repo:
    repo = git.Repo.clone_from(git_url, dir_path, depth=1)
    return repo


def get_github_repo_url(owner: str, name: str, token: Optional[str] = None) -> str:
    base_host = "github.com"
    if token:
        base_host = f"{token}@{base_host}"

    return f"https://{base_host}/{owner}/{name}"
