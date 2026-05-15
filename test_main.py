"""Unit tests for git utility functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from main import run_git, init_repo, get_status, get_log, get_branches, create_branch


def make_temp_repo() -> str:
    """Create a temporary git repository and return its path."""
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "init"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "config", "gpg.program", ""], cwd=tmp, capture_output=True)
    return tmp


class TestRunGit:
    def test_valid_command(self, tmp_path):
        code, out, err = run_git(["init"], cwd=str(tmp_path))
        assert code == 0

    def test_invalid_command(self, tmp_path):
        code, out, err = run_git(["not-a-real-subcommand"], cwd=str(tmp_path))
        assert code != 0


class TestInitRepo:
    def test_creates_new_repo(self, tmp_path):
        target = str(tmp_path / "new_repo")
        assert init_repo(target) is True
        assert (Path(target) / ".git").exists()

    def test_existing_directory(self, tmp_path):
        assert init_repo(str(tmp_path)) is True


class TestGetStatus:
    def test_clean_repo(self):
        path = make_temp_repo()
        # Create and commit a file so HEAD exists
        (Path(path) / "a.txt").write_text("hello")
        subprocess.run(["git", "add", "a.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=path, capture_output=True)
        assert get_status(path) == "Clean working tree"

    def test_untracked_file(self):
        path = make_temp_repo()
        (Path(path) / "untracked.txt").write_text("hi")
        status = get_status(path)
        assert "untracked.txt" in status


class TestGetLog:
    def test_no_commits(self):
        path = make_temp_repo()
        assert get_log(path) == []

    def test_with_commits(self):
        path = make_temp_repo()
        (Path(path) / "f.txt").write_text("x")
        subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "first commit"], cwd=path, capture_output=True)
        log = get_log(path)
        assert len(log) == 1
        assert "first commit" in log[0]


class TestGetBranches:
    def test_no_branches_before_commit(self):
        path = make_temp_repo()
        assert get_branches(path) == []

    def test_main_branch_after_commit(self):
        path = make_temp_repo()
        (Path(path) / "f.txt").write_text("x")
        subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=path, capture_output=True)
        branches = get_branches(path)
        assert len(branches) >= 1


class TestCreateBranch:
    def test_create_branch(self):
        path = make_temp_repo()
        (Path(path) / "f.txt").write_text("x")
        subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=path, capture_output=True)
        assert create_branch("feature/test", path) is True
        branches = get_branches(path)
        assert "feature/test" in branches
