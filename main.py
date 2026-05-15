#!/usr/bin/env python3
"""Simple git repository manager utility."""

import subprocess
import sys
from pathlib import Path


def run_git(args: list[str], cwd: str = ".") -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def init_repo(path: str) -> bool:
    """Initialize a new git repository at the given path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    code, out, err = run_git(["init"], cwd=path)
    if code == 0:
        print(f"Initialized repository at {path}")
        return True
    print(f"Error: {err}", file=sys.stderr)
    return False


def get_status(path: str = ".") -> str:
    """Return the git status of a repository."""
    code, out, err = run_git(["status", "--short"], cwd=path)
    if code != 0:
        return f"Error: {err}"
    return out or "Clean working tree"


def get_log(path: str = ".", count: int = 10) -> list[str]:
    """Return the last `count` commit messages."""
    code, out, _ = run_git(
        ["log", f"-{count}", "--oneline"], cwd=path
    )
    if code != 0 or not out:
        return []
    return out.splitlines()


def get_branches(path: str = ".") -> list[str]:
    """List all local branches."""
    code, out, _ = run_git(["branch", "--format=%(refname:short)"], cwd=path)
    if code != 0 or not out:
        return []
    return out.splitlines()


def create_branch(name: str, path: str = ".") -> bool:
    """Create a new branch."""
    code, _, err = run_git(["checkout", "-b", name], cwd=path)
    if code == 0:
        print(f"Created and switched to branch '{name}'")
        return True
    print(f"Error: {err}", file=sys.stderr)
    return False


def commit_all(message: str, path: str = ".") -> bool:
    """Stage all changes and create a commit."""
    run_git(["add", "-A"], cwd=path)
    code, _, err = run_git(["commit", "-m", message], cwd=path)
    if code == 0:
        print(f"Committed: {message}")
        return True
    print(f"Error: {err}", file=sys.stderr)
    return False


def main() -> None:
    """Demo: report status and recent log of the current repository."""
    path = "."
    print("=== Git Status ===")
    print(get_status(path))

    print("\n=== Recent Commits ===")
    log = get_log(path, count=5)
    if log:
        for entry in log:
            print(f"  {entry}")
    else:
        print("  No commits yet")

    print("\n=== Branches ===")
    branches = get_branches(path)
    if branches:
        for branch in branches:
            print(f"  {branch}")
    else:
        print("  No branches found")


if __name__ == "__main__":
    main()
