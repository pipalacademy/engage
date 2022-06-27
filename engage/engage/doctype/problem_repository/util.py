import os
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import git
import requests


PathString = Union[str, os.PathLike]


def get_github_repo_url(owner: str, name: str, token: Optional[str] = None) -> str:
    base_host = "github.com"
    if token:
        base_host = f"{token}@{base_host}"

    return f"https://{base_host}/{owner}/{name}"


def shallow_clone(git_url: str, dir_path: PathString, branch: str) -> git.Repo:
    repo = git.Repo.clone_from(git_url, dir_path, branch=branch, depth=1)
    return repo


def get_commit_hash(repo: git.Repo) -> str:
    return repo.head.commit.hexsha


def flatten_to_tuples(dl: Dict[str, List]) -> Iterator[Tuple[Any, Any]]:
    for key in dl:
        for val in dl[key]:
            yield (key, val)


def get_default_branch(repo_owner: str, repo_name: str, token: str = None) -> str:
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers.update({"Authorization": f"Bearer {token}"})

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()["default_branch"]


def get_latest_commit(repo_owner: str, repo_name: str, branch: str, token: str = None) -> str:
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{branch}"
    headers = {"Accept": "application/vnd.github.v3.sha"}
    if token:
        headers.update({"Authorization": f"Bearer {token}"})

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.text
