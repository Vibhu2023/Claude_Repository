#!/usr/bin/env python3
"""Daily hiring pipeline status report generator for Moolchand Healthcare Group."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Pipeline data — update statuses here as candidates progress
# ---------------------------------------------------------------------------

PIPELINE: dict = {
    "org": "Moolchand Healthcare Group",
    "hiring_manager": "Vibhu Talwar",
    "generated": "2026-05-19",
    "positions": [
        {
            "id": "FIN-001",
            "title": "Sr Finance Manager / Finance & AR Lead",
            "target": 2,
            "hired": 1,
            "candidates": [
                {
                    "id": "FIN-JAT-001",
                    "name": "Jatin Sachdeva",
                    "status": "HIRED",
                    "score": 7.2,
                    "offer": "₹4.5L",
                    "joining": "June 18, 2026",
                    "source": "GIST Consulting",
                    "contact": "",
                    "note": "Confirmed joining",
                },
                {
                    "id": "FIN-RAH-001",
                    "name": "CA Rahul Madaan",
                    "status": "PRIMARY",
                    "score": 8.8,
                    "offer": "₹42-44L",
                    "notice": "30 days",
                    "est_start": "Mid-June 2026",
                    "source": "GIST Consulting",
                    "contact": "9873060422 | rahulmadaan942@gmail.com",
                    "note": "ONLY viable option — contact TODAY",
                    "priority": 1,
                },
                {
                    "id": "FIN-MAN-001",
                    "name": "CA Manu Singla",
                    "status": "BACKUP",
                    "score": 8.9,
                    "note": "Too junior (3 years)",
                },
                {
                    "id": "FIN-JAT-002",
                    "name": "CA Jatin Anand",
                    "status": "BACKUP",
                    "score": 8.5,
                    "note": "6 years experience",
                },
                {
                    "id": "FIN-KAP-001",
                    "name": "CA Kapil Sharma",
                    "status": "BACKUP",
                    "score": 7.8,
                    "note": "7 years experience",
                },
                {
                    "id": "FIN-RIT-001",
                    "name": "Ritu Arora",
                    "status": "BACKUP",
                    "score": 8.2,
                    "note": "7 years; high CTC ₹31.67L",
                },
                {
                    "id": "FIN-SHU-001",
                    "name": "Shukla Satia",
                    "status": "BACKUP",
                    "score": 7.8,
                    "note": "6 years experience",
                },
                {
                    "id": "FIN-ABH-001",
                    "name": "CA Abhishek Goyal",
                    "status": "REJECTED",
                    "score": 9.3,
                    "note": "Declined offer despite highest score",
                },
                {
                    "id": "FIN-VIK-001",
                    "name": "Vikas Jain",
                    "status": "REJECTED",
                    "score": 7.5,
                    "note": "Rejected by Moolchand — SAP gap + weak AR/C2C",
                },
            ],
        },
        {
            "id": "RPA-001",
            "title": "RPA Developer",
            "target": 2,
            "hired": 0,
            "candidates": [
                {
                    "id": "RPA-RIT-001",
                    "name": "Ritik Gupta",
                    "status": "BACKED_OUT",
                    "score": 8.8,
                    "note": "Was confirmed hired — withdrew after acceptance",
                },
                {
                    "id": "RPA-KAM-001",
                    "name": "Kamal",
                    "status": "PRIMARY",
                    "score": 7.8,
                    "offer": "₹6.6L",
                    "notice": "90 days (negotiate to 60)",
                    "est_start": "July 2026",
                    "source": "GIST — Hemant Kulasri",
                    "contact": "Via GIST — Hemant Kulasri",
                    "note": "UiPath Orchestrator expert — contact THIS WEEK",
                    "priority": 3,
                },
                {
                    "id": "RPA-ANS-001",
                    "name": "Anshul Vashisth",
                    "status": "PRIMARY",
                    "score": 8.8,
                    "offer": "₹6L + ₹2-3L SAP training",
                    "notice": "Immediate",
                    "est_start": "July 2026",
                    "source": "Internal",
                    "contact": "From resume",
                    "note": "SAP FICO integration — contact WEEK 2 (May 27-28)",
                    "priority": 4,
                },
                {
                    "id": "RPA-SHA-001",
                    "name": "Shahe Faisal",
                    "status": "OPTIONAL",
                    "score": 8.5,
                    "offer": "₹13-15L",
                    "notice": "15 days",
                    "source": "PDF (May 18)",
                    "note": "Premium tier — Capgemini Rising Star; needs budget approval",
                },
                {
                    "id": "RPA-SUB-001",
                    "name": "Subrat",
                    "status": "EXCLUDED",
                    "note": "Tier 3 — limited enterprise experience",
                },
                {
                    "id": "RPA-JAS-001",
                    "name": "Jasmin Bar",
                    "status": "EXCLUDED",
                    "note": "Tier 3 — limited enterprise experience",
                },
                {
                    "id": "RPA-HAR-001",
                    "name": "Hardik Agarwal",
                    "status": "EXCLUDED",
                    "note": "Junior — mentorship-pair only",
                },
            ],
        },
        {
            "id": "DRO-001",
            "title": "Chief Digital Revenue Officer",
            "target": 1,
            "hired": 0,
            "candidates": [
                {
                    "id": "DRO-KUW-001",
                    "name": "Kuwarjeet Sidana",
                    "status": "PRIMARY",
                    "score": 9.5,
                    "offer": "₹28L",
                    "notice": "30 days",
                    "est_start": "June 15-30, 2026",
                    "source": "GIST Consulting",
                    "contact": "8800100021 | kuwarjeetsingh18@gmail.com",
                    "note": "ONLY candidate — NO BACKUP — must close this week",
                    "priority": 2,
                },
            ],
        },
    ],
}

# ---------------------------------------------------------------------------
# Status display config
# ---------------------------------------------------------------------------

STATUS_ICON = {
    "HIRED": "✅",
    "PRIMARY": "📞",
    "BACKUP": "📋",
    "OPTIONAL": "💰",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "BACKED_OUT": "⚠️",
    "ON_HOLD": "⏸️",
}

STATUS_LABEL = {
    "HIRED": "HIRED",
    "PRIMARY": "PRIMARY",
    "BACKUP": "BACKUP",
    "OPTIONAL": "PREMIUM OPT",
    "EXCLUDED": "EXCLUDED",
    "REJECTED": "REJECTED",
    "BACKED_OUT": "BACKED OUT",
    "ON_HOLD": "ON HOLD",
}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _divider(char: str = "-", width: int = 68) -> str:
    return char * width


def _count_by_status(positions: list) -> dict:
    counts: dict[str, int] = {}
    for pos in positions:
        for c in pos["candidates"]:
            s = c["status"]
            counts[s] = counts.get(s, 0) + 1
    return counts


def _get_priorities(positions: list) -> list:
    """Return candidates with a 'priority' field, sorted by priority."""
    items = []
    for pos in positions:
        for c in pos["candidates"]:
            if "priority" in c:
                items.append((c["priority"], pos["title"], c))
    return sorted(items, key=lambda x: x[0])


def generate_report(pipeline: dict = PIPELINE, *, save: bool = True) -> str:
    """Build and optionally save the daily status report. Returns the report text."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M %p")

    lines: list[str] = []
    add = lines.append

    add(_divider("="))
    add(f"  {pipeline['org'].upper()} — DAILY HIRING PIPELINE STATUS")
    add(_divider("="))
    add(f"  Date: {today}  |  Updated: {time_str}")
    add(f"  Hiring Manager: {pipeline['hiring_manager']}")
    add(_divider())

    # Summary counts
    counts = _count_by_status(pipeline["positions"])
    total_candidates = sum(
        len(p["candidates"]) for p in pipeline["positions"]
    )
    total_positions = sum(p["target"] for p in pipeline["positions"])
    total_hired = sum(p["hired"] for p in pipeline["positions"])
    need = total_positions - total_hired

    add("")
    add("OVERALL SUMMARY")
    add(_divider())
    add(
        f"  Open Positions: {total_positions}  |  Hired: {total_hired}  "
        f"|  Still Needed: {need}"
    )
    add(f"  Total Candidates: {total_candidates}")
    for status, count in sorted(counts.items()):
        icon = STATUS_ICON.get(status, "  ")
        label = STATUS_LABEL.get(status, status)
        add(f"  {icon}  {label}: {count}")

    # Priority actions
    priorities = _get_priorities(pipeline["positions"])
    if priorities:
        add("")
        add("TODAY'S PRIORITY ACTIONS")
        add(_divider())
        for rank, pos_title, c in priorities:
            icon = STATUS_ICON.get(c["status"], "📌")
            contact = c.get("contact", "")
            note = c.get("note", "")
            offer = c.get("offer", "")
            add(f"  [{rank}] {icon} {c['name']}  ({pos_title})")
            if offer:
                add(f"       Offer: {offer}")
            if contact:
                add(f"       Contact: {contact}")
            if note:
                add(f"       Note: {note}")

    # Per-position detail
    add("")
    add("POSITION STATUS DETAIL")
    add(_divider())
    for pos in pipeline["positions"]:
        need_pos = pos["target"] - pos["hired"]
        status_tag = "✅ FILLED" if need_pos == 0 else f"⚠️  NEED {need_pos} MORE"
        add("")
        add(
            f"  [{pos['id']}]  {pos['title']}"
            f"  |  Target: {pos['target']}  |  {status_tag}"
        )
        add(f"  {'-' * 60}")

        for c in pos["candidates"]:
            icon = STATUS_ICON.get(c["status"], "  ")
            label = STATUS_LABEL.get(c["status"], c["status"])
            score_str = f"  Score: {c['score']}/10" if "score" in c else ""
            offer_str = f"  |  Offer: {c['offer']}" if "offer" in c else ""
            start_str = (
                f"  |  Est. Start: {c['est_start']}" if "est_start" in c else ""
            )
            join_str = (
                f"  |  Joining: {c['joining']}" if "joining" in c else ""
            )
            contact_str = (
                f"\n       Contact: {c['contact']}" if c.get("contact") else ""
            )
            note_str = (
                f"\n       Note: {c.get('note', '')}" if c.get("note") else ""
            )
            add(
                f"  {icon} [{label}]  {c['name']}"
                f"{score_str}{offer_str}{start_str}{join_str}"
                f"{contact_str}{note_str}"
            )

    # Cost summary
    add("")
    add("COST SUMMARY")
    add(_divider())
    add("  Committed:")
    add("    Jatin Sachdeva (Finance)  ₹4.5L  ✅ HIRED")
    add("")
    add("  Estimated remaining hires:")
    add("    Finance  — CA Rahul Madaan    ₹42-44L")
    add("    RPA #1   — Kamal              ₹6.6L")
    add("    RPA #2   — Anshul Vashisth   ₹6L + ₹2-3L training")
    add("    DRO      — Kuwarjeet Sidana  ₹28L")
    add("                                  ─────────────")
    add("                          TOTAL  ₹89-91L  (+ ₹4.5L committed)")

    # Key risks
    add("")
    add("KEY RISKS")
    add(_divider())
    add("  🔴 DRO-001: Kuwarjeet Sidana — NO BACKUP candidate (CRITICAL)")
    add("  🟠 RPA-001: Both primaries have competing offers; fast-track contacts")
    add("  🟡 FIN-001: Rahul is only viable primary; backups available if needed")
    add("  🟡 Timeline pressure — Jatin starts June 18; others mid-June to July")

    # Next review
    add("")
    add(_divider())
    add(f"  Report auto-generated: {today} {time_str}")
    add("  Next full review: May 26, 2026  (post-primary outreach)")
    add(_divider("="))

    report = "\n".join(lines)

    if save:
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / f"pipeline_{today}.md"
        report_path.write_text(f"```\n{report}\n```\n", encoding="utf-8")
        print(f"Report saved → {report_path}")

    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    report = generate_report(save=True)
    print(report)


if __name__ == "__main__":
    main()
