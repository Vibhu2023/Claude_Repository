#!/usr/bin/env python3
"""Generate daily hiring pipeline status report."""

import subprocess
from datetime import date

REPORT_FILE = "HIRING_PIPELINE_REPORT.md"
STATUS_FILE = "DAILY_PIPELINE_STATUS.md"

CANDIDATES = {
    "Finance": {
        "hired": [
            {"name": "Jatin Sachdeva", "id": "FIN-JAT-001", "score": 7.2,
             "status": "HIRED", "joining": "June 18, 2026", "offer": "₹4.5L"},
        ],
        "primary": [
            {"name": "CA Rahul Madaan", "id": "FIN-RAH-001", "score": 8.8,
             "status": "PRIMARY", "offer": "₹42-44L", "contact": "9873060422"},
        ],
        "backup": [
            {"name": "CA Manu Singla", "id": "FIN-MAN-001", "score": 8.9, "status": "BACKUP"},
            {"name": "CA Jatin Anand", "id": "FIN-JAT-002", "score": 8.5, "status": "BACKUP"},
            {"name": "CA Kapil Sharma", "id": "FIN-KAP-001", "score": 7.8, "status": "BACKUP"},
            {"name": "Ritu Arora", "id": "FIN-RIT-001", "score": 8.2, "status": "BACKUP"},
            {"name": "Shukla Satia", "id": "FIN-SHU-001", "score": 7.8, "status": "BACKUP"},
        ],
        "rejected": [
            {"name": "CA Abhishek Goyal", "id": "FIN-ABH-001", "score": 9.3,
             "status": "DECLINED", "reason": "Declined offer"},
            {"name": "Vikas Jain", "id": "FIN-VIK-001", "score": 7.5,
             "status": "REJECTED", "reason": "SAP inexperience + weak AR/C2C"},
        ],
    },
    "RPA": {
        "primary": [
            {"name": "Kamal", "id": "RPA-KAM-001", "score": 7.8,
             "status": "PRIMARY", "offer": "₹6.6L", "contact": "Via GIST - Hemant Kulasri"},
            {"name": "Anshul Vashisth", "id": "RPA-ANS-001", "score": 8.8,
             "status": "PRIMARY", "offer": "₹6L + ₹2-3L training", "contact": "Internal"},
        ],
        "optional": [
            {"name": "Shahe Faisal", "id": "RPA-SHA-001", "score": 8.5,
             "status": "OPTIONAL", "offer": "₹13-15L", "note": "Premium if budget approved"},
        ],
        "backed_out": [
            {"name": "Ritik Gupta", "id": "RPA-RIT-001", "score": 8.8,
             "status": "BACKED OUT", "reason": "Withdrew after acceptance"},
        ],
        "do_not_contact": [
            {"name": "Subrat", "id": "RPA-SUB-001", "status": "EXCLUDED"},
            {"name": "Jasmin Bar", "id": "RPA-JAS-001", "status": "EXCLUDED"},
            {"name": "Hardik Agarwal", "id": "RPA-HAR-001", "status": "EXCLUDED"},
        ],
    },
    "DRO": {
        "primary": [
            {"name": "Kuwarjeet Sidana", "id": "DRO-KUW-001", "score": 9.5,
             "status": "PRIMARY", "offer": "₹28L", "contact": "8800100021",
             "note": "ONLY CANDIDATE - NO BACKUP"},
        ],
    },
}

TIMELINE = [
    ("May 19-20, 2026", "Contact Rahul (Finance) + Kuwarjeet (DRO)"),
    ("May 20-21, 2026", "Outreach Kamal (RPA #1) via GIST"),
    ("May 27-28, 2026", "Contact Anshul Vashisth (RPA #2)"),
    ("June 15-30, 2026", "Kuwarjeet Sidana joins (DRO)"),
    ("June 18, 2026", "Jatin Sachdeva joins (Finance) ✓"),
    ("July 2026", "Kamal + Anshul expected start (RPA)"),
]


def compute_metrics():
    hired = len(CANDIDATES["Finance"]["hired"])
    primary = (
        len(CANDIDATES["Finance"]["primary"])
        + len(CANDIDATES["RPA"]["primary"])
        + len(CANDIDATES["DRO"]["primary"])
    )
    backup = len(CANDIDATES["Finance"]["backup"])
    optional = len(CANDIDATES["RPA"]["optional"])
    backed_out = len(CANDIDATES["RPA"]["backed_out"])
    rejected = len(CANDIDATES["Finance"]["rejected"])
    excluded = len(CANDIDATES["RPA"]["do_not_contact"])
    total = hired + primary + backup + optional + backed_out + rejected + excluded
    return {
        "total": total,
        "hired": hired,
        "primary": primary,
        "backup": backup,
        "optional": optional,
        "backed_out": backed_out,
        "rejected": rejected,
        "excluded": excluded,
    }


def generate_report(today: str) -> str:
    m = compute_metrics()
    lines = [
        f"# Moolchand Healthcare Group — Daily Pipeline Status",
        f"**Date:** {today}  ",
        f"**Hiring Manager:** Vibhu Talwar  ",
        f"**Auto-generated at:** 10:00 AM IST  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Candidates Tracked | {m['total']} |",
        f"| **Hired** | {m['hired']} |",
        f"| **Primary (Active)** | {m['primary']} |",
        f"| **Backup** | {m['backup']} |",
        f"| Optional (Premium) | {m['optional']} |",
        f"| Backed Out | {m['backed_out']} |",
        f"| Rejected / Declined | {m['rejected']} |",
        f"| Excluded (Do Not Contact) | {m['excluded']} |",
        "",
        "---",
        "",
        "## Position Status",
        "",
        "### Finance & AR Lead (FIN-001) — 2 positions needed",
        "",
        "| Candidate | ID | Score | Status | Offer | Notes |",
        "|-----------|-----|-------|--------|-------|-------|",
    ]

    for c in CANDIDATES["Finance"]["hired"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | ✅ {c['status']} | {c['offer']} | Joining {c['joining']} |"
        )
    for c in CANDIDATES["Finance"]["primary"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | 🎯 {c['status']} | {c['offer']} | Contact: {c['contact']} |"
        )
    for c in CANDIDATES["Finance"]["backup"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | 🔵 {c['status']} | — | Standby |"
        )
    for c in CANDIDATES["Finance"]["rejected"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | ❌ {c['status']} | — | {c.get('reason', '')} |"
        )

    lines += [
        "",
        "### RPA Developer (RPA-001) — 2 positions needed",
        "",
        "| Candidate | ID | Score | Status | Offer | Notes |",
        "|-----------|-----|-------|--------|-------|-------|",
    ]

    for c in CANDIDATES["RPA"]["primary"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | 🎯 {c['status']} | {c['offer']} | {c.get('contact', '')} |"
        )
    for c in CANDIDATES["RPA"]["optional"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | 💰 {c['status']} | {c['offer']} | {c.get('note', '')} |"
        )
    for c in CANDIDATES["RPA"]["backed_out"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | ⚠️ {c['status']} | — | {c.get('reason', '')} |"
        )

    lines += [
        "",
        "### Chief Digital Revenue Officer (DRO-001) — 1 position needed",
        "",
        "| Candidate | ID | Score | Status | Offer | Notes |",
        "|-----------|-----|-------|--------|-------|-------|",
    ]

    for c in CANDIDATES["DRO"]["primary"]:
        lines.append(
            f"| {c['name']} | {c['id']} | {c['score']}/10 | 🎯 {c['status']} | {c['offer']} | ⚠️ {c.get('note', '')} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Key Risks",
        "",
        "| Risk | Level | Mitigation |",
        "|------|-------|------------|",
        "| Rahul Madaan unavailable (Finance) | Medium | 5 backup candidates ready |",
        "| RPA market competition | Medium | Fast-track this week; Shahe Faisal fallback |",
        "| DRO no backup candidate | **CRITICAL** | Must close Kuwarjeet this week |",
        "| Compressed hiring timeline | High | Parallel outreach + onboarding prep now |",
        "",
        "---",
        "",
        "## Upcoming Milestones",
        "",
        "| Date | Action |",
        "|------|--------|",
    ]

    for date_str, action in TIMELINE:
        lines.append(f"| {date_str} | {action} |")

    lines += [
        "",
        "---",
        "",
        "## Immediate Actions Required",
        "",
        "1. **Finance:** Confirm status of CA Rahul Madaan outreach (offer ₹42-44L)",
        "2. **DRO:** Follow up with Kuwarjeet Sidana — NO backup exists (offer ₹28L)",
        "3. **RPA #1:** Check Kamal outreach progress via GIST (Hemant Kulasri)",
        "4. **RPA #2:** Initiate contact with Anshul Vashisth (offer ₹6L + training)",
        "5. **Onboarding:** Prepare Jatin Sachdeva onboarding for June 18, 2026",
        "",
        "---",
        "",
        f"*Auto-generated daily status report — {today} 10:00 AM IST*  ",
        f"*Source data: HIRING_PIPELINE_REPORT.md (last manual update: May 19, 2026)*",
    ]

    return "\n".join(lines)


def git_push(filepath: str, today: str):
    subprocess.run(["git", "add", filepath], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("No changes to commit.")
        return
    msg = f"chore: daily pipeline status update {today}"
    subprocess.run(["git", "commit", "-m", msg], check=True)
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=True
    ).stdout.strip()
    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
    print(f"Pushed to {branch}")


def main():
    today = date.today().isoformat()
    report = generate_report(today)
    with open(STATUS_FILE, "w") as f:
        f.write(report)
    print(f"Written: {STATUS_FILE}")
    git_push(STATUS_FILE, today)


if __name__ == "__main__":
    main()
