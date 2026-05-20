#!/usr/bin/env python3
"""Daily 10 AM hiring pipeline status update for Moolchand Healthcare Group."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


# ── data model ──────────────────────────────────────────────────────────────

@dataclass
class Candidate:
    id: str
    name: str
    position: str
    position_id: str
    score: float
    status: str          # HIRED | PRIMARY | BACKUP | OPTIONAL | ON_HOLD | EXCLUDED | REJECTED | WITHDRAWN | BACKED_OUT
    ctc: str
    notice_days: Optional[int] = None
    est_start: Optional[date] = None
    joining_date: Optional[date] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    source: str = ""
    action_deadline: Optional[date] = None   # date by which action should be taken
    notes: str = ""
    priority: int = 99   # lower = more urgent


@dataclass
class Pipeline:
    generated: date
    hiring_manager: str
    positions: list[dict] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)


# ── pipeline data ────────────────────────────────────────────────────────────

def load_pipeline() -> Pipeline:
    """Return the current candidate pipeline (single source of truth)."""
    p = Pipeline(
        generated=date(2026, 5, 19),
        hiring_manager="Vibhu Talwar",
        positions=[
            {"id": "FIN-001", "title": "Sr Finance Manager / Finance & AR Lead", "target": 2, "hired": 1},
            {"id": "RPA-001", "title": "RPA Developer", "target": 2, "hired": 0},
            {"id": "DRO-001", "title": "Chief Digital Revenue Officer", "target": 1, "hired": 0},
        ],
    )

    p.candidates = [
        # ── Finance ─────────────────────────────────────────────────────────
        Candidate(
            id="FIN-JAT-001", name="Jatin Sachdeva", position="Sr Finance Manager",
            position_id="FIN-001", score=7.2, status="HIRED", ctc="₹4.5L",
            joining_date=date(2026, 6, 18),
            source="GIST Consulting",
            notes="4 yrs general accounting. Joining confirmed.",
            priority=5,
        ),
        Candidate(
            id="FIN-RAH-001", name="CA Rahul Madaan", position="Sr Finance Manager",
            position_id="FIN-001", score=8.8, status="PRIMARY", ctc="₹42-44L",
            notice_days=30, est_start=date(2026, 6, 15),
            contact_email="rahulmadaan942@gmail.com", contact_phone="9873060422",
            source="GIST Consulting",
            action_deadline=date(2026, 5, 20),
            notes="Only viable finance option. 8 yrs; ECSO, CarDekho, BDO, Mazars. SAP+Tally.",
            priority=1,
        ),
        Candidate(
            id="FIN-MAN-001", name="CA Manu Singla", position="Sr Finance Manager",
            position_id="FIN-001", score=8.9, status="BACKUP", ctc="TBD",
            notes="Too junior (3 yrs). Use only if Rahul unavailable.", priority=20,
        ),
        Candidate(
            id="FIN-JAT-002", name="CA Jatin Anand", position="Sr Finance Manager",
            position_id="FIN-001", score=8.5, status="BACKUP", ctc="TBD",
            notes="6 yrs experience.", priority=21,
        ),
        Candidate(
            id="FIN-KAP-001", name="CA Kapil Sharma", position="Sr Finance Manager",
            position_id="FIN-001", score=7.8, status="BACKUP", ctc="TBD",
            notes="7 yrs experience.", priority=22,
        ),
        Candidate(
            id="FIN-RIT-001", name="Ritu Arora", position="Sr Finance Manager",
            position_id="FIN-001", score=8.2, status="BACKUP", ctc="₹31.67L",
            notes="7 yrs; high CTC ask.", priority=23,
        ),
        Candidate(
            id="FIN-SHU-001", name="Shukla Satia", position="Sr Finance Manager",
            position_id="FIN-001", score=7.8, status="BACKUP", ctc="TBD",
            notes="6 yrs experience.", priority=24,
        ),
        Candidate(
            id="FIN-ABH-001", name="CA Abhishek Goyal", position="Sr Finance Manager",
            position_id="FIN-001", score=9.3, status="REJECTED",
            ctc="N/A", notes="Highest score (9.3). Declined offer.", priority=99,
        ),
        Candidate(
            id="FIN-VIK-001", name="Vikas Jain", position="Sr Finance Manager",
            position_id="FIN-001", score=7.5, status="REJECTED", ctc="N/A",
            notes="SAP inexperience + weak AR/C2C. Rejected by Moolchand.", priority=99,
        ),

        # ── RPA ─────────────────────────────────────────────────────────────
        Candidate(
            id="RPA-RIT-001", name="Ritik Gupta", position="RPA Developer",
            position_id="RPA-001", score=8.8, status="BACKED_OUT", ctc="N/A",
            notes="Was confirmed hired. Withdrew after acceptance. Major setback.", priority=99,
        ),
        Candidate(
            id="RPA-KAM-001", name="Kamal", position="RPA Developer",
            position_id="RPA-001", score=7.8, status="PRIMARY", ctc="₹6.6L",
            notice_days=90, est_start=date(2026, 7, 1),
            source="GIST Consulting (via Hemant Kulasri)",
            action_deadline=date(2026, 5, 21),
            notes="UiPath Orchestrator 5/5. Negotiate notice 90→60 days.",
            priority=3,
        ),
        Candidate(
            id="RPA-ANS-001", name="Anshul Vashisth", position="RPA Developer",
            position_id="RPA-001", score=8.8, status="PRIMARY", ctc="₹6L + ₹2-3L training",
            notice_days=0, est_start=date(2026, 7, 1),
            source="Internal",
            action_deadline=date(2026, 5, 28),
            notes="SAP FICO + UiPath. Immediate joiner. Critical SAP HANA advantage.",
            priority=4,
        ),
        Candidate(
            id="RPA-SHA-001", name="Shahe Faisal", position="RPA Developer",
            position_id="RPA-001", score=8.5, status="OPTIONAL", ctc="₹13-15L",
            notice_days=15,
            source="PDF (May 18)",
            notes="Capgemini. Competing offers Cognizant/TCS ₹13L. Premium tier only.",
            priority=10,
        ),
        Candidate(
            id="RPA-SUB-001", name="Subrat", position="RPA Developer",
            position_id="RPA-001", score=0.0, status="EXCLUDED", ctc="N/A",
            notes="DO NOT SEND. Limited enterprise experience.", priority=99,
        ),
        Candidate(
            id="RPA-JAS-001", name="Jasmin Bar", position="RPA Developer",
            position_id="RPA-001", score=0.0, status="EXCLUDED", ctc="N/A",
            notes="DO NOT SEND. Limited enterprise experience.", priority=99,
        ),
        Candidate(
            id="RPA-HAR-001", name="Hardik Agarwal", position="RPA Developer",
            position_id="RPA-001", score=0.0, status="EXCLUDED", ctc="N/A",
            notes="Junior. Mentorship-pair only.", priority=99,
        ),

        # ── DRO ─────────────────────────────────────────────────────────────
        Candidate(
            id="DRO-KUW-001", name="Kuwarjeet Sidana", position="Chief Digital Revenue Officer",
            position_id="DRO-001", score=9.5, status="PRIMARY", ctc="₹28L",
            notice_days=30, est_start=date(2026, 6, 15),
            contact_email="kuwarjeetsingh18@gmail.com", contact_phone="8800100021",
            source="GIST Consulting",
            action_deadline=date(2026, 5, 21),
            notes="9.5/10. Only candidate — NO BACKUP. Fortis 3.5yr. 130Cr digital revenue.",
            priority=2,
        ),
    ]
    return p


# ── helpers ──────────────────────────────────────────────────────────────────

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🔴",
    "BACKUP": "🟡",
    "OPTIONAL": "🔵",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}

URGENCY_LABEL = {1: "CRITICAL TODAY", 2: "CRITICAL TODAY", 3: "THIS WEEK",
                 4: "NEXT WEEK", 5: "CONFIRMED", 10: "OPTIONAL"}


def days_until(target: date, today: date) -> int:
    return (target - today).days


def urgency_flag(c: Candidate, today: date) -> str:
    if c.status not in ("PRIMARY", "HIRED"):
        return ""
    if c.action_deadline:
        d = days_until(c.action_deadline, today)
        if d < 0:
            return f"⚠️  OVERDUE by {abs(d)} day(s)"
        if d == 0:
            return "🚨 ACTION DUE TODAY"
        return f"⏰ Action in {d} day(s)"
    return ""


def joining_flag(c: Candidate, today: date) -> str:
    if c.joining_date:
        d = days_until(c.joining_date, today)
        if d < 0:
            return f"Joined {abs(d)} day(s) ago"
        return f"{d} days to joining"
    if c.est_start:
        d = days_until(c.est_start, today)
        if d < 0:
            return f"Est. start was {abs(d)} day(s) ago"
        return f"Est. start in {d} days"
    return ""


# ── report generation ────────────────────────────────────────────────────────

def generate_report(pipeline: Pipeline, today: date) -> str:
    lines: list[str] = []
    a = lines.append

    a(f"# Moolchand Healthcare – Daily Pipeline Status")
    a(f"**Report Date:** {today.strftime('%B %d, %Y')} | Generated at 10:00 AM")
    a(f"**Hiring Manager:** {pipeline.hiring_manager}")
    a("")

    # ── Position fill summary ────────────────────────────────────────────────
    a("## Position Fill Status")
    a("")
    a("| Position | Target | Hired | Remaining | Status |")
    a("|----------|--------|-------|-----------|--------|")
    for pos in pipeline.positions:
        remaining = pos["target"] - pos["hired"]
        status_icon = "✅ FILLED" if remaining == 0 else ("🔴 URGENT" if remaining > 0 else "❓")
        a(f"| {pos['title']} | {pos['target']} | {pos['hired']} | {remaining} | {status_icon} |")
    a("")

    # ── Action items (PRIMARY candidates only) ───────────────────────────────
    primaries = sorted(
        [c for c in pipeline.candidates if c.status == "PRIMARY"],
        key=lambda c: c.priority,
    )
    a("## 🚨 Immediate Action Items")
    a("")
    for c in primaries:
        uflag = urgency_flag(c, today)
        jflag = joining_flag(c, today)
        a(f"### [{c.priority}] {c.name} — {c.position}")
        a(f"- **Status:** {STATUS_EMOJI['PRIMARY']} PRIMARY  {uflag}")
        a(f"- **Score:** {c.score}/10  |  **CTC:** {c.ctc}")
        if c.contact_email:
            a(f"- **Email:** {c.contact_email}  |  **Phone:** {c.contact_phone}")
        if c.source:
            a(f"- **Source:** {c.source}")
        if c.notice_days is not None:
            a(f"- **Notice Period:** {c.notice_days} days  |  {jflag}")
        if c.action_deadline:
            d = days_until(c.action_deadline, today)
            label = "TODAY" if d == 0 else (f"in {d} days" if d > 0 else f"OVERDUE {abs(d)}d")
            a(f"- **Action Deadline:** {c.action_deadline.strftime('%b %d')} ({label})")
        a(f"- **Notes:** {c.notes}")
        a("")

    # ── Hired / Confirmed ────────────────────────────────────────────────────
    hired = [c for c in pipeline.candidates if c.status == "HIRED"]
    if hired:
        a("## ✅ Confirmed Hires")
        a("")
        for c in hired:
            jflag = joining_flag(c, today)
            a(f"- **{c.name}** ({c.position}) — CTC {c.ctc} — {jflag}")
        a("")

    # ── Full candidate table ─────────────────────────────────────────────────
    a("## Full Candidate Pipeline")
    a("")
    a("| ID | Name | Position | Score | Status | CTC | Key Date |")
    a("|----|------|----------|-------|--------|-----|----------|")

    active_statuses = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD"}
    for c in sorted(pipeline.candidates, key=lambda x: (x.priority, x.name)):
        if c.status not in active_statuses:
            continue
        emoji = STATUS_EMOJI.get(c.status, "")
        key_date = ""
        if c.joining_date:
            key_date = f"Join {c.joining_date.strftime('%b %d')}"
        elif c.est_start:
            key_date = f"Start ~{c.est_start.strftime('%b %d')}"
        elif c.action_deadline:
            key_date = f"Action by {c.action_deadline.strftime('%b %d')}"
        a(f"| {c.id} | {c.name} | {c.position} | {c.score}/10 | {emoji} {c.status} | {c.ctc} | {key_date} |")
    a("")

    # ── Rejected / withdrawn summary ─────────────────────────────────────────
    inactive = [c for c in pipeline.candidates if c.status not in active_statuses]
    if inactive:
        a("## Inactive Candidates")
        a("")
        a("| Name | Position | Status | Reason |")
        a("|------|----------|--------|--------|")
        for c in inactive:
            emoji = STATUS_EMOJI.get(c.status, "")
            a(f"| {c.name} | {c.position} | {emoji} {c.status} | {c.notes[:60]} |")
        a("")

    # ── Risk summary ─────────────────────────────────────────────────────────
    a("## Risk Snapshot")
    a("")

    # DRO has no backup
    dro_primary = [c for c in pipeline.candidates if c.position_id == "DRO-001" and c.status == "PRIMARY"]
    dro_backup = [c for c in pipeline.candidates if c.position_id == "DRO-001" and c.status == "BACKUP"]
    if dro_primary and not dro_backup:
        a("- 🔴 **DRO — NO BACKUP**: Single candidate (Kuwarjeet). Must close this week.")

    # Overdue actions
    overdue = [
        c for c in pipeline.candidates
        if c.action_deadline and days_until(c.action_deadline, today) < 0 and c.status == "PRIMARY"
    ]
    for c in overdue:
        d = abs(days_until(c.action_deadline, today))
        a(f"- ⚠️  **{c.name}** — action deadline passed {d} day(s) ago. Follow up immediately.")

    # RPA still 0 hired
    rpa_hired = [c for c in pipeline.candidates if c.position_id == "RPA-001" and c.status == "HIRED"]
    if not rpa_hired:
        a("- 🔴 **RPA — 0 hired**: Ritik Gupta backed out. Dual-hire Kamal + Anshul this week.")

    a("")

    # ── Timeline ─────────────────────────────────────────────────────────────
    a("## Upcoming Timeline")
    a("")
    events = [
        (date(2026, 5, 20), "Contact Rahul Madaan (Finance offer)"),
        (date(2026, 5, 20), "Contact Kuwarjeet Sidana (DRO interview)"),
        (date(2026, 5, 21), "Outreach Kamal via GIST (RPA #1)"),
        (date(2026, 5, 27), "Contact Anshul Vashisth (RPA #2)"),
        (date(2026, 6, 15), "Kuwarjeet Sidana expected start (DRO)"),
        (date(2026, 6, 18), "Jatin Sachdeva joins (Finance)"),
        (date(2026, 7, 1),  "Kamal + Anshul expected start (RPA)"),
    ]
    for ev_date, ev_desc in sorted(events):
        d = days_until(ev_date, today)
        if d < -1:
            marker = f"~~{ev_date.strftime('%b %d')}~~ (past)"
        elif d == 0:
            marker = f"**{ev_date.strftime('%b %d')} — TODAY ←**"
        elif d <= 3:
            marker = f"**{ev_date.strftime('%b %d')}** ({d}d away)"
        else:
            marker = f"{ev_date.strftime('%b %d')} ({d}d away)"
        a(f"- {marker}: {ev_desc}")
    a("")

    a("---")
    a(f"*Next review: {(today + timedelta(days=1)).strftime('%B %d, %Y')} at 10:00 AM*")

    return "\n".join(lines)


# ── output / save ─────────────────────────────────────────────────────────────

def save_report(report: str, output_path: Path) -> None:
    output_path.write_text(report, encoding="utf-8")
    print(f"Report saved → {output_path}")


def print_report(report: str) -> None:
    print(report)


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    today = date.today()

    # Allow overriding date for testing: --date YYYY-MM-DD
    if "--date" in args:
        idx = args.index("--date")
        today = date.fromisoformat(args[idx + 1])

    save_to_file = "--save" in args or "-s" in args
    quiet = "--quiet" in args or "-q" in args

    pipeline = load_pipeline()
    report = generate_report(pipeline, today)

    if not quiet:
        print_report(report)

    if save_to_file:
        repo_root = Path(__file__).parent
        out_path = repo_root / "DAILY_PIPELINE_STATUS.md"
        save_report(report, out_path)


if __name__ == "__main__":
    main()
