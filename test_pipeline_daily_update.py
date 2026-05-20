"""Tests for pipeline_daily_update.py"""

from datetime import date
import pytest
from pipeline_daily_update import (
    load_pipeline,
    generate_report,
    days_until,
    urgency_flag,
    joining_flag,
)


@pytest.fixture
def pipeline():
    return load_pipeline()


@pytest.fixture
def today():
    return date(2026, 5, 20)


# ── data integrity ────────────────────────────────────────────────────────────

def test_all_candidates_have_required_fields(pipeline):
    for c in pipeline.candidates:
        assert c.id, f"Missing id: {c.name}"
        assert c.name
        assert c.status in {
            "HIRED", "PRIMARY", "BACKUP", "OPTIONAL",
            "ON_HOLD", "EXCLUDED", "REJECTED", "WITHDRAWN", "BACKED_OUT"
        }, f"Unknown status for {c.name}: {c.status}"


def test_hired_candidates_have_joining_date(pipeline):
    for c in pipeline.candidates:
        if c.status == "HIRED":
            assert c.joining_date is not None, f"{c.name} is HIRED but has no joining_date"


def test_primary_candidates_have_action_deadline(pipeline):
    for c in pipeline.candidates:
        if c.status == "PRIMARY":
            assert c.action_deadline is not None, (
                f"{c.name} is PRIMARY but has no action_deadline"
            )


def test_unique_candidate_ids(pipeline):
    ids = [c.id for c in pipeline.candidates]
    assert len(ids) == len(set(ids)), "Duplicate candidate IDs found"


def test_scores_in_range(pipeline):
    for c in pipeline.candidates:
        assert 0 <= c.score <= 10, f"{c.name} has out-of-range score {c.score}"


# ── helpers ────────────────────────────────────────────────────────────────────

def test_days_until_future(today):
    future = date(2026, 6, 18)
    assert days_until(future, today) == 29


def test_days_until_past(today):
    past = date(2026, 5, 15)
    assert days_until(past, today) == -5


def test_days_until_same_day(today):
    assert days_until(today, today) == 0


def test_urgency_flag_overdue(pipeline, today):
    # Rahul's deadline is May 20 — same as today → "ACTION DUE TODAY"
    rahul = next(c for c in pipeline.candidates if c.id == "FIN-RAH-001")
    flag = urgency_flag(rahul, today)
    assert "ACTION DUE TODAY" in flag or "OVERDUE" in flag or "Action in" in flag


def test_urgency_flag_non_primary_empty(pipeline, today):
    rejected = next(c for c in pipeline.candidates if c.status == "REJECTED")
    assert urgency_flag(rejected, today) == ""


def test_joining_flag_hired(pipeline):
    jatin = next(c for c in pipeline.candidates if c.id == "FIN-JAT-001")
    flag = joining_flag(jatin, date(2026, 5, 20))
    assert "29 days to joining" == flag


def test_joining_flag_past(pipeline):
    jatin = next(c for c in pipeline.candidates if c.id == "FIN-JAT-001")
    flag = joining_flag(jatin, date(2026, 6, 20))
    assert "Joined" in flag and "ago" in flag


# ── report generation ──────────────────────────────────────────────────────────

def test_report_contains_header(pipeline, today):
    report = generate_report(pipeline, today)
    assert "Moolchand Healthcare" in report
    assert "May 20, 2026" in report
    assert "10:00 AM" in report


def test_report_contains_all_primaries(pipeline, today):
    report = generate_report(pipeline, today)
    primaries = [c for c in pipeline.candidates if c.status == "PRIMARY"]
    for c in primaries:
        assert c.name in report, f"{c.name} missing from report"


def test_report_contains_risk_section(pipeline, today):
    report = generate_report(pipeline, today)
    assert "Risk Snapshot" in report
    assert "NO BACKUP" in report


def test_report_dro_no_backup_warning(pipeline, today):
    report = generate_report(pipeline, today)
    assert "DRO" in report
    assert "NO BACKUP" in report


def test_report_rpa_zero_hired_warning(pipeline, today):
    report = generate_report(pipeline, today)
    assert "0 hired" in report


def test_report_upcoming_timeline(pipeline, today):
    report = generate_report(pipeline, today)
    assert "Upcoming Timeline" in report
    assert "Jatin Sachdeva joins" in report


def test_report_inactive_candidates_section(pipeline, today):
    report = generate_report(pipeline, today)
    assert "Inactive Candidates" in report
    assert "REJECTED" in report or "BACKED_OUT" in report


def test_report_position_fill_table(pipeline, today):
    report = generate_report(pipeline, today)
    assert "Position Fill Status" in report
    assert "Sr Finance Manager" in report
    assert "RPA Developer" in report
    assert "Chief Digital Revenue Officer" in report


def test_report_future_date(pipeline):
    future_today = date(2026, 7, 15)
    report = generate_report(pipeline, future_today)
    # All action deadlines are in the past — overdue warnings should appear
    assert "OVERDUE" in report or "past" in report


def test_report_past_date_preserves_structure(pipeline):
    early_today = date(2026, 5, 1)
    report = generate_report(pipeline, early_today)
    assert "Immediate Action Items" in report
    assert "Full Candidate Pipeline" in report
