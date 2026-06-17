#!/usr/bin/env python3
"""
Daily pipeline status generator for Moolchand Healthcare Group hiring.
Run daily at 10 AM to refresh DAILY_STATUS_UPDATE.md.
"""

from datetime import date, datetime
from pathlib import Path


# Pipeline data — update candidate statuses here as they progress
CANDIDATES = {
    "finance": {
        "target": 2,
        "candidates": [
            {"name": "Jatin Sachdeva", "id": "FIN-JAT-001", "status": "HIRED",
             "offer": "₹4.5L", "joining": "June 18, 2026", "contact": ""},
            {"name": "CA Rahul Madaan", "id": "FIN-RAH-001", "status": "PENDING",
             "offer": "₹42-44L", "contact": "rahulmadaan942@gmail.com / 9873060422"},
            {"name": "CA Manu Singla", "id": "FIN-MAN-001", "status": "BACKUP",
             "offer": "TBD", "contact": ""},
            {"name": "CA Jatin Anand", "id": "FIN-JAT-002", "status": "BACKUP",
             "offer": "TBD", "contact": ""},
            {"name": "CA Kapil Sharma", "id": "FIN-KAP-001", "status": "BACKUP",
             "offer": "TBD", "contact": ""},
        ],
    },
    "rpa": {
        "target": 2,
        "candidates": [
            {"name": "Ritik Gupta", "id": "RPA-RIT-001", "status": "BACKED_OUT",
             "offer": "", "contact": ""},
            {"name": "Kamal", "id": "RPA-KAM-001", "status": "PENDING",
             "offer": "₹6.6L", "contact": "Via GIST — Hemant Kulasri"},
            {"name": "Anshul Vashisth", "id": "RPA-ANS-001", "status": "PENDING",
             "offer": "₹6L + ₹2-3L training", "contact": "Internal"},
            {"name": "Shahe Faisal", "id": "RPA-SHA-001", "status": "OPTIONAL",
             "offer": "₹13-15L", "contact": "Via GIST"},
        ],
    },
    "dro": {
        "target": 1,
        "candidates": [
            {"name": "Kuwarjeet Sidana", "id": "DRO-KUW-001", "status": "PENDING",
             "offer": "₹28L", "joining_window": "June 15-30, 2026",
             "contact": "kuwarjeetsingh18@gmail.com / 8800100021"},
        ],
    },
}

STATUS_ICONS = {
    "HIRED": "✅",
    "PENDING": "⏳",
    "BACKUP": "🔵",
    "OPTIONAL": "🟡",
    "BACKED_OUT": "❌",
    "REJECTED": "❌",
    "WITHDRAWN": "❌",
    "DO_NOT_SEND": "🚫",
}


def count_by_status(candidates, statuses):
    return sum(1 for c in candidates if c["status"] in statuses)


def generate_report():
    today = date.today().strftime("%B %d, %Y")
    tomorrow = date.today().strftime("%B %d, %Y")  # used for labels

    lines = [
        "# Hiring Pipeline — Daily Status Update",
        f"**Date:** {today} | **Time:** 10:00 AM  ",
        "**Hiring Manager:** Vibhu Talwar | **Moolchand Healthcare Group**",
        "",
        "---",
        "",
        "## Position-by-Position Status",
        "",
    ]

    total_target = total_hired = total_pending = 0

    for dept, data in CANDIDATES.items():
        dept_names = {"finance": "Finance / AR Lead (FIN-001)",
                      "rpa": "RPA Developer (RPA-001)",
                      "dro": "Chief Digital Revenue Officer (DRO-001)"}
        lines.append(f"### {dept_names[dept]}")
        lines.append("")
        lines.append("| Candidate | Status | Contact |")
        lines.append("|-----------|--------|---------|")

        for c in data["candidates"]:
            icon = STATUS_ICONS.get(c["status"], "❓")
            contact = c.get("contact", "") or "—"
            lines.append(f"| {c['name']} | {icon} {c['status']} | {contact} |")

        hired = count_by_status(data["candidates"], ["HIRED"])
        pending = count_by_status(data["candidates"], ["PENDING"])
        open_slots = data["target"] - hired
        total_target += data["target"]
        total_hired += hired
        total_pending += pending
        lines += ["", f"**Open slots:** {open_slots} / {data['target']}", ""]

    lines += [
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total positions | {total_target} |",
        f"| Hired / Confirmed | {total_hired} |",
        f"| Pending decisions | {total_pending} |",
        f"| Open slots | {total_target - total_hired} |",
        "",
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        "Source: HIRING_PIPELINE_REPORT.md*",
    ]

    return "\n".join(lines)


def main():
    report = generate_report()
    output_path = Path(__file__).parent / "DAILY_STATUS_UPDATE.md"
    output_path.write_text(report)
    print(f"Daily status written to {output_path}")


if __name__ == "__main__":
    main()
