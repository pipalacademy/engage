import os
from typing import Optional, Union

import git


PathString = Union[str, os.PathLike]


def get_github_repo_url(owner: str, name: str, token: Optional[str] = None) -> str:
    base_host = "github.com"
    if token:
        base_host = f"{token}@{base_host}"

    return f"https://{base_host}/{owner}/{name}"


def shallow_clone(git_url: str, dir_path: PathString) -> git.Repo:
    repo = git.Repo.clone_from(git_url, dir_path, depth=1)
    return repo
