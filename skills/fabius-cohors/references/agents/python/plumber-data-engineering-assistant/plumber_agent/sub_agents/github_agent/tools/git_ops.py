"""
This module provides a set of Git operations tools for an agent.

It includes functions for initializing repositories, checking status,
adding files, committing changes, and managing branches.
"""

import logging
import os
from typing import Any

import git
from git import InvalidGitRepositoryError, Repo

logger = logging.getLogger("plumber-agent")


def initialize_git_repo(repo_path: str) -> dict[str, Any]:
    """
    Initializes a Git repository at a specified path.

    If a repository already exists at the path, it confirms its existence.
    If the path does not exist, it returns an error. If the path exists but is not a Git repo,
    it initializes a new one.

    Args:
        repo_path (str): The local file system path where the repository should be initialized.

    Returns:
        Dict[str, Any]: A dictionary containing the status of the operation.
                        On success, includes 'status', 'message', 'is_existing',
                        and 'current_branch'.
                        On failure, includes 'status' and 'message'.
    """
    try:
        if not os.path.exists(repo_path):
            return {
                "status": "error",
                "message": f"Path does not exist: {repo_path}",
            }
        try:
            existing_repo = Repo(repo_path)
            return {
                "status": "success",
                "message": f"Git repository already exists at {repo_path}",
                "is_existing": True,
                "current_branch": existing_repo.active_branch.name,
            }
        except InvalidGitRepositoryError as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            repo = Repo.init(repo_path)
            return {
                "status": "success",
                "message": f"Git repository initialized at {repo_path}",
                "is_existing": False,
                "current_branch": "main" if repo.heads else "No commits yet",
            }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to initialize Git repository: {e!s}",
        }


def get_git_status(repo_path: str) -> dict[str, Any]:
    """
    Retrieves the status of a Git repository.

    This includes the current branch, modified files, staged files, and untracked files.
    It also provides a summary of whether the repository is dirty and the total number of changes.

    Args:
        repo_path (str): The path to the local Git repository.

    Returns:
        Dict[str, Any]: A dictionary detailing the repository's status, including lists
                        of modified, staged, and untracked files. On error, returns a
                        dictionary with 'status' and 'message'.
    """
    try:
        repo = Repo(repo_path)
        try:
            has_commits = bool(list(repo.iter_commits(max_count=1)))
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("An error occurred: %s", e, exc_info=True)
            has_commits = False
        modified_files = [item.a_path for item in repo.index.diff(None)]
        if has_commits:
            try:
                staged_files = [item.a_path for item in repo.index.diff("HEAD")]
                current_branch = repo.active_branch.name
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("An error occurred: %s", e, exc_info=True)
                staged_files = list(repo.index.entries.keys())
                current_branch = "main"
        else:
            staged_files = list(repo.index.entries.keys())
            try:
                current_branch = repo.active_branch.name
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("An error occurred: %s", e, exc_info=True)
                try:
                    current_branch = repo.git.branch("--show-current").strip()
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logger.error("An error occurred: %s", err, exc_info=True)
                    current_branch = "main"
        untracked_files = repo.untracked_files
        return {
            "status": "success",
            "current_branch": current_branch,
            "has_commits": has_commits,
            "is_dirty": repo.is_dirty(),
            "modified_files": modified_files,
            "staged_files": staged_files,
            "untracked_files": list(untracked_files),
            "total_changes": len(modified_files)
            + len(staged_files)
            + len(untracked_files),
        }
    except InvalidGitRepositoryError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Not a Git repository: {repo_path}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get Git status: {e!s}",
        }


def add_files_to_git(
    repo_path: str, files: list[str] | None = None, add_all: bool = False
) -> dict[str, Any]:
    """
    Adds specified files or all changes to the Git staging area.

    Args:
        repo_path (str): The path to the local Git repository.
        files (Optional[List[str]], optional): A list of file paths relative to the repo root
                                               to add to the staging area. Defaults to None.
        add_all (bool, optional): If True, stages all modified and untracked files ('git add -A').
                                  Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing the status of the operation and a list of
                        files that were added. On error, returns a dictionary with 'status'
                        and 'message'.
    """
    try:
        repo = Repo(repo_path)
        if add_all:
            repo.git.add(A=True)
            added_files = "All modified and untracked files"
        elif files:
            valid_files = []
            for file_path in files:
                full_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_path):
                    valid_files.append(file_path)
                else:
                    return {
                        "status": "error",
                        "message": f"File not found: {file_path}",
                    }
            repo.index.add(valid_files)
            added_files = valid_files
        else:
            return {
                "status": "error",
                "message": "No files specified and add_all is False",
            }
        return {
            "status": "success",
            "message": "Files added to staging area successfully",
            "added_files": added_files,
        }
    except InvalidGitRepositoryError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Not a Git repository: {repo_path}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {"status": "error", "message": f"Failed to add files: {e!s}"}


def commit_changes(
    repo_path: str,
    commit_message: str,
    author_name: str = "",
    author_email: str = "",
) -> dict[str, Any]:
    """
    Commits staged changes in the repository.

    Args:
        repo_path (str): The path to the local Git repository.
        commit_message (str): The message for the commit.
        author_name (str, optional): The name of the commit author. Defaults to "".
        author_email (str, optional): The email of the commit author. Defaults to "".

    Returns:
        Dict[str, Any]: A dictionary with the operation status, commit hash, and other
                        details. On error, returns a dictionary with 'status' and 'message'.
    """
    try:
        repo = Repo(repo_path)
        try:
            has_commits = bool(list(repo.iter_commits(max_count=1)))
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("An error occurred: %s", e, exc_info=True)
            has_commits = False
        if has_commits:
            if not repo.index.diff("HEAD"):
                return {
                    "status": "error",
                    "message": "No staged changes to commit",
                }
        elif not repo.index.entries:
            return {
                "status": "error",
                "message": "No staged changes to commit",
            }
        if author_name and author_email:
            author = git.Actor(author_name, author_email)
            commit = repo.index.commit(commit_message, author=author)
        else:
            commit = repo.index.commit(commit_message)
        return {
            "status": "success",
            "message": "Changes committed successfully",
            "commit_hash": commit.hexsha[:8],
            "commit_message": commit_message,
            "files_changed": len(commit.stats.files),
        }
    except InvalidGitRepositoryError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Not a Git repository: {repo_path}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to commit changes: {e!s}",
        }


def list_git_branches(repo_path: str) -> dict[str, Any]:
    """
    Lists all local branches in a Git repository.

    Args:
        repo_path (str): The path to the local Git repository.

    Returns:
        Dict[str, Any]: A dictionary containing the list of branches, the current branch,
                        and the total count of branches. On error, returns a dictionary
                        with 'status' and 'message'.
    """
    try:
        repo = Repo(repo_path)
        branches = []
        current_branch = None
        for branch in repo.heads:
            branch_info = {
                "name": branch.name,
                "is_current": branch == repo.active_branch,
            }
            if branch_info["is_current"]:
                current_branch = branch.name
            branches.append(branch_info)
        return {
            "status": "success",
            "current_branch": current_branch,
            "branches": branches,
            "total_branches": len(branches),
        }
    except InvalidGitRepositoryError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Not a Git repository: {repo_path}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {"status": "error", "message": f"Failed to list branches: {e!s}"}


def switch_git_branch(
    repo_path: str, branch_name: str, create_if_not_exists: bool = False
) -> dict[str, Any]:
    """
    Switches to a different Git branch or creates a new one.

    It will prevent switching if there are uncommitted changes in the repository.

    Args:
        repo_path (str): The path to the local Git repository.
        branch_name (str): The name of the branch to switch to.
        create_if_not_exists (bool, optional): If True, a new branch will be created
                                               if the specified branch does not exist.
                                               Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary with the operation status. On success, it indicates
                        if a new branch was created. On error, returns a dictionary
                        with 'status' and 'message'.
    """
    try:
        repo = Repo(repo_path)
        if repo.is_dirty():
            msg = (
                "Cannot switch branches with uncommitted changes. "
                "Please commit or stash changes first."
            )
            return {
                "status": "error",
                "message": msg,
            }
        try:
            repo.git.checkout(branch_name)
            return {
                "status": "success",
                "message": f"Switched to existing branch '{branch_name}'",
                "current_branch": branch_name,
                "created_new": False,
            }
        except git.exc.GitCommandError as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            if create_if_not_exists:
                repo.git.checkout("-b", branch_name)
                return {
                    "status": "success",
                    "message": f"Created and switched to new branch '{branch_name}'",
                    "current_branch": branch_name,
                    "created_new": True,
                }

            msg = (
                f"Branch '{branch_name}' does not exist. "
                "Set create_if_not_exists=True to create it."
            )
            return {
                "status": "error",
                "message": msg,
            }
    except InvalidGitRepositoryError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Not a Git repository: {repo_path}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", e, exc_info=True)
        return {"status": "error", "message": f"Failed to switch branch: {e!s}"}
