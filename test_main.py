"""Unit tests for git utility functions and daily pipeline status report."""

import json
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from main import run_git, init_repo, get_status, get_log, get_branches, create_branch
from daily_status import load_data, count_by_status, candidates_needing_action, render_report, DATA_FILE


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


class TestDailyStatus:
    IST = timezone(timedelta(hours=5, minutes=30))

    def _sample_data(self) -> dict:
        return {
            "meta": {"organization": "Test Org", "hiring_manager": "Test User", "last_updated": "2026-05-19"},
            "positions": [
                {"id": "FIN-001", "title": "Finance Lead", "target_headcount": 2, "hired": 1, "needed": 1, "urgency": "URGENT"}
            ],
            "candidates": [
                {"id": "C1", "name": "Alice", "position_id": "FIN-001", "position_title": "Finance",
                 "status": "HIRED", "score": 8.0, "action_required": "Onboard", "action_deadline": "THIS WEEK",
                 "email": None, "phone": None, "target_offer": None, "est_start": None},
                {"id": "C2", "name": "Bob", "position_id": "FIN-001", "position_title": "Finance",
                 "status": "PRIMARY", "score": 9.0, "action_required": "Call today",
                 "action_deadline": "TODAY", "email": "bob@example.com", "phone": "9999999999",
                 "target_offer": "₹10L", "est_start": "June 2026"},
                {"id": "C3", "name": "Carol", "position_id": "FIN-001", "position_title": "Finance",
                 "status": "REJECTED", "score": 6.0, "action_required": None, "action_deadline": None},
            ]
        }

    def test_load_data_returns_dict(self):
        data = load_data()
        assert isinstance(data, dict)
        assert "candidates" in data
        assert "positions" in data

    def test_count_by_status(self):
        data = self._sample_data()
        counts = count_by_status(data["candidates"])
        assert counts["HIRED"] == 1
        assert counts["PRIMARY"] == 1
        assert counts["REJECTED"] == 1

    def test_candidates_needing_action(self):
        data = self._sample_data()
        urgent = candidates_needing_action(data["candidates"])
        names = [c["name"] for c in urgent]
        assert "Alice" in names   # HIRED with action
        assert "Bob" in names     # PRIMARY with action
        assert "Carol" not in names  # REJECTED, no action

    def test_render_report_contains_key_sections(self):
        data = self._sample_data()
        now = datetime(2026, 5, 22, 10, 0, 0, tzinfo=self.IST)
        report = render_report(data, now)
        assert "Executive Summary" in report
        assert "Actions Required Today" in report
        assert "Position Breakdown" in report
        assert "Alice" in report
        assert "Bob" in report
        assert "bob@example.com" in report

    def test_render_report_date_appears(self):
        data = self._sample_data()
        now = datetime(2026, 5, 22, 10, 0, 0, tzinfo=self.IST)
        report = render_report(data, now)
        assert "May 22, 2026" in report

    def test_render_report_progress_bar(self):
        data = self._sample_data()
        now = datetime(2026, 5, 22, 10, 0, 0, tzinfo=self.IST)
        report = render_report(data, now)
        assert "1/2 filled" in report
