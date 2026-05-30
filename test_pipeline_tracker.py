"""Unit tests for pipeline_tracker module."""

import datetime
from unittest.mock import patch, MagicMock

import pytest

from pipeline_tracker import (
    CANDIDATES,
    POSITIONS,
    Candidate,
    Position,
    generate_status_report,
    print_status_report,
    run_daily_scheduler,
)


class TestDataIntegrity:
    def test_all_candidates_have_valid_position(self):
        pos_ids = {p.id for p in POSITIONS}
        for c in CANDIDATES:
            assert c.position in pos_ids, f"{c.id} references unknown position {c.position}"

    def test_hired_count_matches_data(self):
        for pos in POSITIONS:
            hired = sum(1 for c in CANDIDATES if c.position == pos.id and c.status == "Hired")
            assert hired == pos.hired, f"{pos.id}: hired field mismatch"

    def test_scores_in_valid_range(self):
        for c in CANDIDATES:
            assert 0.0 <= c.score <= 10.0, f"{c.id} has invalid score {c.score}"

    def test_position_remaining(self):
        for pos in POSITIONS:
            assert pos.remaining == pos.target - pos.hired


class TestGenerateStatusReport:
    def test_returns_string(self):
        assert isinstance(generate_status_report(), str)

    def test_contains_position_ids(self):
        report = generate_status_report()
        for pos in POSITIONS:
            assert pos.id in report

    def test_contains_primary_candidate_names(self):
        report = generate_status_report()
        for c in CANDIDATES:
            if c.status == "Primary":
                assert c.name in report

    def test_contains_contact_info(self):
        report = generate_status_report()
        assert "rahulmadaan942@gmail.com" in report
        assert "kuwarjeetsingh18@gmail.com" in report

    def test_custom_date(self):
        d = datetime.date(2026, 6, 1)
        report = generate_status_report(report_date=d)
        assert "June 01, 2026" in report

    def test_default_date_is_today(self):
        today = datetime.date.today()
        report = generate_status_report()
        assert today.strftime("%B %d, %Y") in report

    def test_cost_summary_present(self):
        report = generate_status_report()
        assert "₹89" in report
        assert "Jatin Sachdeva" in report

    def test_header_present(self):
        report = generate_status_report()
        assert "MOOLCHAND HEALTHCARE GROUP" in report
        assert "HIRING PIPELINE STATUS" in report

    def test_priority_actions_section(self):
        report = generate_status_report()
        assert "TODAY'S PRIORITY ACTIONS" in report

    def test_status_breakdown_section(self):
        report = generate_status_report()
        assert "CANDIDATE STATUS BREAKDOWN" in report


class TestPrintStatusReport:
    def test_prints_to_stdout(self, capsys):
        print_status_report()
        captured = capsys.readouterr()
        assert "MOOLCHAND HEALTHCARE GROUP" in captured.out


class TestRunDailyScheduler:
    def test_schedules_job_and_runs(self):
        with patch("pipeline_tracker.schedule") as mock_sched, \
             patch("pipeline_tracker.time.sleep", side_effect=KeyboardInterrupt):
            mock_every = MagicMock()
            mock_sched.every.return_value = mock_every
            mock_every.day.at.return_value.do.return_value = None
            mock_sched.run_pending.return_value = None

            with pytest.raises(KeyboardInterrupt):
                run_daily_scheduler("10:00")

            mock_sched.every.return_value.day.at.assert_called_once_with("10:00")

    def test_custom_time(self):
        with patch("pipeline_tracker.schedule") as mock_sched, \
             patch("pipeline_tracker.time.sleep", side_effect=KeyboardInterrupt):
            mock_every = MagicMock()
            mock_sched.every.return_value = mock_every
            mock_every.day.at.return_value.do.return_value = None

            with pytest.raises(KeyboardInterrupt):
                run_daily_scheduler("09:30")

            mock_sched.every.return_value.day.at.assert_called_once_with("09:30")
