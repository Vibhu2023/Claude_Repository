#!/usr/bin/env python3
"""
Daily hiring pipeline status updater for Moolchand Healthcare Group.
Generates a snapshot of candidate statuses from HIRING_PIPELINE_REPORT.md.
Designed to run at 10:00 AM IST via GitHub Actions cron.
"""

import os
import re
from datetime import date

REPORT_FILE = "HIRING_PIPELINE_REPORT.md"
STATUS_FILE = "DAILY_STATUS.md"
HISTORY_FILE = "STATUS_HISTORY.md"

POSITIONS = [
    {
        "id": "FIN-001",
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": 1,
        "needed": 1,
        "alert": "🔴 URGENT",
        "primaries": [
            {
                "name": "CA Rahul Madaan",
                "score": "8.8/10",
                "offer": "₹42-44L",
                "email": "rahulmadaan942@gmail.com",
                "phone": "9873060422",
                "notice": "30 days",
                "est_start": "Mid-June 2026",
                "action": "Follow up on offer — ONLY viable option",
                "priority": "P1 TODAY",
            }
        ],
        "hired_list": [
            {
                "name": "Jatin Sachdeva",
                "offer": "₹4.5L",
                "joining": "June 18, 2026",
                "note": "CONFIRMED ✓",
            }
        ],
        "backups": [
            "CA Manu Singla (8.9/10)",
            "CA Jatin Anand (8.5/10)",
            "CA Kapil Sharma (7.8/10)",
            "Ritu Arora (8.2/10)",
            "Shukla Satia (7.8/10)",
        ],
    },
    {
        "id": "RPA-001",
        "title": "RPA Developer",
        "target": 2,
        "hired": 0,
        "needed": 2,
        "alert": "🚨 CRITICAL",
        "note": "Ritik Gupta backed out after offer acceptance — 0/2 hired",
        "primaries": [
            {
                "name": "Kamal",
                "score": "7.8/10",
                "offer": "₹6.6L",
                "contact": "Via GIST — Hemant Kulasri",
                "notice": "90 days (negotiate to 60)",
                "est_start": "July 2026",
                "action": "Outreach via GIST this week",
                "priority": "P2 THIS WEEK",
                "skill_highlight": "UiPath Orchestrator (5/5) | Enterprise bot scaling",
            },
            {
                "name": "Anshul Vashisth",
                "score": "8.8/10",
                "offer": "₹6L + ₹2-3L SAP training",
                "notice": "Immediate",
                "est_start": "July 2026",
                "action": "Schedule outreach — Week 2",
                "priority": "P2 WEEK 2",
                "skill_highlight": "SAP FICO integration | Critical for HANA deployment",
            },
        ],
        "optional": {
            "name": "Shahe Faisal",
            "score": "8.5/10",
            "offer": "₹13-15L",
            "note": "Premium tier — budget approval required",
        },
        "backups": [],
    },
    {
        "id": "DRO-001",
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": 0,
        "needed": 1,
        "alert": "🚨 CRITICAL — NO BACKUP",
        "primaries": [
            {
                "name": "Kuwarjeet Sidana",
                "score": "9.5/10",
                "offer": "₹28L",
                "email": "kuwarjeetsingh18@gmail.com",
                "phone": "8800100021",
                "notice": "30 days",
                "est_start": "June 15-30, 2026",
                "action": "Follow up on interview — must close soon",
                "priority": "P1 TODAY",
                "skill_highlight": "10 yrs exp | 3.5 yrs healthcare | 130+ Cr digital revenue at Fortis",
            }
        ],
        "backups": [],
    },
]

OVERALL = {
    "total_candidates": 27,
    "open_positions": 3,
    "hired": 1,
    "primary": 4,
    "backup": 5,
    "optional": 1,
    "on_hold": 2,
    "excluded": 2,
    "rejected": 7,
    "withdrawn": 1,
    "backed_out": 1,
    "total_cost_remaining": "₹89-91L",
}


def days_until(target_date_str):
    """Return days until a target date string like '2026-06-18'."""
    try:
        target = date.fromisoformat(target_date_str)
        delta = (target - date.today()).days
        if delta < 0:
            return f"{abs(delta)} days ago"
        elif delta == 0:
            return "TODAY"
        elif delta == 1:
            return "TOMORROW"
        else:
            return f"in {delta} days"
    except ValueError:
        return target_date_str


def generate_position_block(pos):
    lines = []
    hired = pos["hired"]
    target = pos["target"]
    needed = pos["needed"]
    progress_bar = "█" * hired + "░" * needed
    lines.append(
        f"### {pos['title']} ({pos['id']}) {pos['alert']}"
    )
    lines.append(
        f"Progress: [{progress_bar}] {hired}/{target} hired — **{needed} still needed**"
    )
    if "note" in pos:
        lines.append(f"> ⚠️ {pos['note']}")
    lines.append("")

    # Hired
    if pos.get("hired_list"):
        lines.append("**Hired:**")
        for h in pos["hired_list"]:
            lines.append(
                f"- ✅ {h['name']} — {h['offer']} — Joining: {h['joining']} ({days_until('2026-06-18')}) — {h['note']}"
            )
        lines.append("")

    # Primaries
    if pos.get("primaries"):
        lines.append("**Primary Candidate(s) — Action Required:**")
        for p in pos["primaries"]:
            contact_parts = []
            if "email" in p:
                contact_parts.append(p["email"])
            if "phone" in p:
                contact_parts.append(p["phone"])
            if "contact" in p:
                contact_parts.append(p["contact"])
            contact_str = " | ".join(contact_parts) if contact_parts else "See report"
            lines.append(
                f"- **{p['name']}** — Score: {p['score']} — Offer: {p['offer']}"
            )
            lines.append(f"  - Contact: {contact_str}")
            lines.append(f"  - Notice: {p['notice']} | Est. Start: {p['est_start']}")
            if "skill_highlight" in p:
                lines.append(f"  - Skills: {p['skill_highlight']}")
            lines.append(f"  - 🏷️ **{p['priority']}** — {p['action']}")
        lines.append("")

    # Optional
    if pos.get("optional"):
        opt = pos["optional"]
        lines.append(
            f"**Optional (Premium):** {opt['name']} — Score: {opt['score']} — Offer: {opt['offer']} — _{opt['note']}_"
        )
        lines.append("")

    # Backups
    if pos.get("backups"):
        lines.append(
            f"**Backup Pool ({len(pos['backups'])}):** "
            + ", ".join(pos["backups"])
        )
        lines.append("")

    return "\n".join(lines)


def generate_report(today):
    lines = [
        f"# Moolchand Healthcare Group — Daily Pipeline Status",
        f"**Date:** {today.strftime('%B %d, %Y')} | **Report Time:** 10:00 AM IST",
        f"**Hiring Manager:** Vibhu Talwar",
        "",
        "---",
        "",
        "## Pipeline Overview",
        "",
        "| Position | Target | Hired | Needed | Alert |",
        "|----------|--------|-------|--------|-------|",
    ]

    for pos in POSITIONS:
        lines.append(
            f"| {pos['title']} ({pos['id']}) | {pos['target']} | {pos['hired']} | {pos['needed']} | {pos['alert']} |"
        )

    lines += [
        "",
        f"**Total Candidates:** {OVERALL['total_candidates']} | "
        f"**Hired:** {OVERALL['hired']} | "
        f"**Active (Primary):** {OVERALL['primary']} | "
        f"**Backup:** {OVERALL['backup']}",
        f"**Estimated Remaining Cost:** {OVERALL['total_cost_remaining']}",
        "",
        "---",
        "",
        "## Position Details",
        "",
    ]

    for pos in POSITIONS:
        lines.append(generate_position_block(pos))
        lines.append("---")
        lines.append("")

    lines += [
        "## Today's Priority Actions",
        "",
        "| Priority | Candidate | Role | Action | Contact |",
        "|----------|-----------|------|--------|---------|",
        "| 🔴 P1 TODAY | CA Rahul Madaan | Finance | Follow up on offer | rahulmadaan942@gmail.com / 9873060422 |",
        "| 🔴 P1 TODAY | Kuwarjeet Sidana | DRO | Follow up on interview | kuwarjeetsingh18@gmail.com / 8800100021 |",
        "| 🟡 P2 THIS WEEK | Kamal | RPA #1 | Outreach via GIST | Hemant Kulasri (GIST) |",
        "| 🟡 P2 WEEK 2 | Anshul Vashisth | RPA #2 | Schedule outreach | From resume |",
        "| 🟢 P3 ONGOING | Jatin Sachdeva | Finance (Hired) | Confirm onboarding | Joining June 18 |",
        "",
        "---",
        "",
        "## Critical Alerts",
        "",
        "- 🚨 **RPA CRITICAL:** 0/2 RPA developers hired. Ritik Gupta backed out. Need 2 urgently for July start.",
        "- ⚠️ **DRO RISK:** Single candidate (Kuwarjeet 9.5/10) — zero backup. Market leverage is high. Must close.",
        f"- 📅 **Next Joining:** Jatin Sachdeva on June 18, 2026 ({days_until('2026-06-18')})",
        "- 💰 **Total Remaining Budget:** ₹89-91L across 4 open positions",
        "",
        "---",
        "",
        "## Candidate Status Breakdown",
        "",
        "| Status | Count | Details |",
        "|--------|-------|---------|",
        f"| ✅ Hired | {OVERALL['hired']} | Jatin Sachdeva (Finance) — Joining June 18 |",
        f"| 🎯 Primary | {OVERALL['primary']} | Rahul (Finance), Kamal (RPA), Anshul (RPA), Kuwarjeet (DRO) |",
        f"| 🔄 Backup | {OVERALL['backup']} | 5 Finance backups (Manu, Jatin A., Kapil, Ritu, Shukla) |",
        f"| 💰 Optional | {OVERALL['optional']} | Shahe Faisal (RPA Premium — ₹13-15L) |",
        f"| ⏸️ On Hold | {OVERALL['on_hold']} | Rajeev Rana, CA Bharat Singh |",
        f"| ❌ Rejected | {OVERALL['rejected']} | 7 candidates across all positions |",
        f"| 🚫 Excluded | {OVERALL['excluded']} | Exceed experience ceiling (6-10 yrs) |",
        f"| 🚪 Backed Out | {OVERALL['backed_out']} | Ritik Gupta (was RPA hire) |",
        f"| 🏃 Withdrawn | {OVERALL['withdrawn']} | Shivani Jain |",
        "",
        "---",
        "",
        "*Auto-generated daily at 10:00 AM IST by pipeline_status.py*",
        "*Source data: HIRING_PIPELINE_REPORT.md (last updated May 19, 2026)*",
        f"*Generated: {today.isoformat()}*",
    ]

    return "\n".join(lines) + "\n"


def update_history(today, report):
    """Append a brief entry to the history log if not already present."""
    today_str = today.isoformat()
    entry = (
        f"\n### {today_str} ({today.strftime('%B %d, %Y')})\n"
        f"- Pipeline: 1 hired | 4 primary active | 4 positions still open\n"
        f"- P1 follow-ups: Rahul Madaan (Finance), Kuwarjeet Sidana (DRO)\n"
        f"- RPA: 0/2 hired — Kamal + Anshul outreach in progress\n"
        f"- Next joining: Jatin Sachdeva — June 18, 2026\n"
    )

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            content = f.read()
        if today_str in content:
            return  # already logged today
        with open(HISTORY_FILE, "a") as f:
            f.write(entry)
    else:
        with open(HISTORY_FILE, "w") as f:
            f.write("# Hiring Pipeline — Daily Status History\n")
            f.write("_Auto-updated each day at 10:00 AM IST_\n")
            f.write(entry)


def main():
    if not os.path.exists(REPORT_FILE):
        print(f"ERROR: {REPORT_FILE} not found. Run from repository root.")
        return 1

    today = date.today()
    report = generate_report(today)

    with open(STATUS_FILE, "w") as f:
        f.write(report)
    print(f"Written: {STATUS_FILE}")

    update_history(today, report)
    print(f"Updated: {HISTORY_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
