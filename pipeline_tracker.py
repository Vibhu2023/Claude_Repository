#!/usr/bin/env python3
"""Daily hiring pipeline status tracker for Moolchand Healthcare Group."""

import datetime
import time
from dataclasses import dataclass, field
from typing import Optional

import schedule


@dataclass
class Candidate:
    id: str
    name: str
    position: str
    score: float
    status: str
    ctc_current: Optional[str] = None
    ctc_offer: Optional[str] = None
    notice_days: Optional[int] = None
    est_start: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: str = ""


@dataclass
class Position:
    id: str
    title: str
    target: int
    hired: int

    @property
    def remaining(self) -> int:
        return self.target - self.hired


CANDIDATES: list[Candidate] = [
    # Finance
    Candidate("FIN-JAT-001", "Jatin Sachdeva", "FIN-001", 7.2, "Hired",
              ctc_offer="₹4.5L", est_start="June 18, 2026",
              notes="CONFIRMED - Confirm onboarding details"),
    Candidate("FIN-RAH-001", "CA Rahul Madaan", "FIN-001", 8.8, "Primary",
              ctc_current="₹35L", ctc_offer="₹42-44L", notice_days=30,
              est_start="Mid-June",
              contact_email="rahulmadaan942@gmail.com", contact_phone="9873060422",
              notes="CONTACT TODAY - Only viable Finance option after rejections"),
    Candidate("FIN-MAN-001", "CA Manu Singla", "FIN-001", 8.9, "Backup",
              notes="Too junior (3 years)"),
    Candidate("FIN-JAT-002", "CA Jatin Anand", "FIN-001", 8.5, "Backup",
              notes="6 years experience"),
    Candidate("FIN-KAP-001", "CA Kapil Sharma", "FIN-001", 7.8, "Backup",
              notes="7 years experience"),
    Candidate("FIN-RIT-001", "Ritu Arora", "FIN-001", 8.2, "Backup",
              notes="7 years, high CTC ₹31.67L"),
    Candidate("FIN-SHU-001", "Shukla Satia", "FIN-001", 7.8, "Backup",
              notes="6 years experience"),
    Candidate("FIN-ABH-001", "CA Abhishek Goyal", "FIN-001", 9.3, "Rejected",
              notes="Declined offer despite highest score (9.3/10)"),
    Candidate("FIN-VIK-001", "Vikas Jain", "FIN-001", 7.5, "Rejected",
              notes="Rejected by Moolchand - SAP inexperience + weak AR/C2C"),
    # RPA
    Candidate("RPA-RIT-001", "Ritik Gupta", "RPA-001", 8.8, "Backed Out",
              notes="Was confirmed hired - withdrew after acceptance"),
    Candidate("RPA-KAM-001", "Kamal", "RPA-001", 7.8, "Primary",
              ctc_offer="₹6.6L", notice_days=90, est_start="July 2026",
              notes="CONTACT THIS WEEK via GIST (Hemant Kulasri) - negotiate 90→60 days notice"),
    Candidate("RPA-ANS-001", "Anshul Vashisth", "RPA-001", 8.8, "Primary",
              ctc_offer="₹6L", notice_days=0, est_start="July 2026",
              notes="CONTACT WEEK 2 - SAP FICO advantage, offer ₹6L + ₹2-3L training"),
    Candidate("RPA-SHA-001", "Shahe Faisal", "RPA-001", 8.5, "Optional",
              ctc_offer="₹13-15L", notice_days=15,
              notes="Premium optional - Capgemini Rising Star, competing offers ₹13L"),
    Candidate("RPA-SUB-001", "Subrat", "RPA-001", 0.0, "Excluded",
              notes="Limited enterprise experience"),
    Candidate("RPA-JAS-001", "Jasmin Bar", "RPA-001", 0.0, "Excluded",
              notes="Limited enterprise experience"),
    Candidate("RPA-HAR-001", "Hardik Agarwal", "RPA-001", 0.0, "Excluded",
              notes="Junior - mentorship-pair only"),
    # DRO
    Candidate("DRO-KUW-001", "Kuwarjeet Sidana", "DRO-001", 9.5, "Primary",
              ctc_current="₹23L", ctc_offer="₹28L", notice_days=30,
              est_start="June 15-30, 2026",
              contact_email="kuwarjeetsingh18@gmail.com", contact_phone="8800100021",
              notes="INTERVIEW THIS WEEK - NO BACKUP - must close at ₹28L"),
]

POSITIONS: list[Position] = [
    Position("FIN-001", "Sr Finance Manager / Finance & AR Lead", target=2, hired=1),
    Position("RPA-001", "RPA Developer", target=2, hired=0),
    Position("DRO-001", "Chief Digital Revenue Officer", target=1, hired=0),
]

_STATUS_ORDER = [
    "Hired", "Primary", "Backup", "Optional",
    "On Hold", "Backed Out", "Withdrawn", "Rejected", "Excluded",
]


def generate_status_report(report_date: Optional[datetime.date] = None) -> str:
    """Generate a formatted daily pipeline status report."""
    if report_date is None:
        report_date = datetime.date.today()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "=" * 62,
        "  MOOLCHAND HEALTHCARE GROUP — HIRING PIPELINE STATUS",
        f"  Date: {report_date.strftime('%B %d, %Y')}   Generated: {now}",
        "=" * 62,
        "",
    ]

    # Position overview
    lines += ["POSITION OVERVIEW", "-" * 40]
    for pos in POSITIONS:
        pos_candidates = [c for c in CANDIDATES if c.position == pos.id]
        primary = [c for c in pos_candidates if c.status == "Primary"]
        hired = [c for c in pos_candidates if c.status == "Hired"]
        if pos.remaining == 0:
            flag = "FILLED "
        elif not primary:
            flag = "CRITICAL"
        else:
            flag = "OPEN   "
        lines.append(f"  [{flag}] {pos.title} ({pos.id})")
        lines.append(
            f"           Target: {pos.target}  Hired: {pos.hired}  "
            f"Still Needed: {pos.remaining}"
        )
        if hired:
            lines.append(f"           Hired:   {', '.join(c.name for c in hired)}")
        if primary:
            lines.append(f"           Primary: {', '.join(c.name for c in primary)}")
        lines.append("")

    # Candidate status breakdown
    lines += ["CANDIDATE STATUS BREAKDOWN", "-" * 40]
    for status in _STATUS_ORDER:
        group = [c for c in CANDIDATES if c.status == status]
        if group:
            names = ", ".join(c.name for c in group)
            lines.append(f"  {status:<12} ({len(group):2d}):  {names}")
    lines.append("")

    # Priority actions — all Primary candidates
    lines += ["TODAY'S PRIORITY ACTIONS", "-" * 40]
    primary_all = [c for c in CANDIDATES if c.status == "Primary"]
    for i, c in enumerate(primary_all, 1):
        lines.append(f"  {i}. {c.name}  [{c.id}]  Score: {c.score}/10")
        if c.contact_email:
            lines.append(f"     Email:     {c.contact_email}")
        if c.contact_phone:
            lines.append(f"     Phone:     {c.contact_phone}")
        if c.ctc_offer:
            lines.append(f"     Offer:     {c.ctc_offer}")
        if c.est_start:
            lines.append(f"     Est Start: {c.est_start}")
        lines.append(f"     Action:    {c.notes}")
        lines.append("")

    # Cost summary
    lines += ["COST SUMMARY", "-" * 40]
    lines += [
        "  Committed:  Jatin Sachdeva (Finance)  ₹4.5L  [HIRED ✓]",
        "  Remaining:  ₹89–91L",
        "    Finance (Rahul Madaan)     ₹42–44L",
        "    RPA #1  (Kamal)            ₹6.6L",
        "    RPA #2  (Anshul Vashisth)  ₹6L + ₹2–3L training",
        "    DRO     (Kuwarjeet Sidana) ₹28L",
        "",
        "=" * 62,
    ]

    return "\n".join(lines)


def print_status_report() -> None:
    """Print the current pipeline status report to stdout."""
    print(generate_status_report())


def run_daily_scheduler(run_at: str = "10:00") -> None:
    """Block and run the pipeline status report every day at `run_at` (HH:MM)."""
    schedule.every().day.at(run_at).do(print_status_report)
    print(f"Pipeline scheduler started — daily report at {run_at}. Press Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    run_daily_scheduler()
