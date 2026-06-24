"""
Daily hiring pipeline status reporter for Moolchand Healthcare Group.
Reads HIRING_PIPELINE_REPORT.md and prints a concise 10 AM status summary.
"""

import re
from datetime import date

REPORT_FILE = "HIRING_PIPELINE_REPORT.md"

POSITIONS = {
    "FIN-001": {
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": [
            {"name": "Jatin Sachdeva", "status": "CONFIRMED", "joining": "June 18, 2026", "ctc": "₹4.5L"},
        ],
        "primary": [
            {"name": "CA Rahul Madaan", "score": 8.8, "ctc": "₹42-44L", "notice": "30 days", "action": "CONTACT TODAY"},
        ],
        "backups": ["CA Manu Singla", "CA Jatin Anand", "CA Kapil Sharma", "Ritu Arora", "Shukla Satia"],
    },
    "RPA-001": {
        "title": "RPA Developer",
        "target": 2,
        "hired": [],
        "primary": [
            {"name": "Kamal", "score": 7.8, "ctc": "₹6.6L", "notice": "90 days (negotiate 60)", "action": "CONTACT THIS WEEK"},
            {"name": "Anshul Vashisth", "score": 8.8, "ctc": "₹6L + ₹2-3L training", "notice": "Immediate", "action": "CONTACT WEEK 2"},
        ],
        "backups": ["Shahe Faisal (premium ₹13-15L if budget approved)"],
        "alert": "CRITICAL: Ritik Gupta backed out after acceptance — 0 developers hired",
    },
    "DRO-001": {
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": [],
        "primary": [
            {"name": "Kuwarjeet Sidana", "score": 9.5, "ctc": "₹28L", "notice": "30 days", "action": "INTERVIEW THIS WEEK"},
        ],
        "backups": [],
        "alert": "WARNING: NO BACKUP candidate — must close this week",
    },
}

OVERALL = {
    "total_positions": 3,
    "total_open": 4,   # 1 more finance + 2 RPA + 1 DRO
    "hired": 1,
    "primary_active": 4,
    "backup_active": 5,
    "total_budget": "₹89-91L",
}


def status_line(label, value, width=28):
    return f"  {label:<{width}} {value}"


def print_report():
    today = date.today().strftime("%A, %B %-d, %Y")
    print("=" * 60)
    print(f"  MOOLCHAND HIRING PIPELINE  —  Daily Status")
    print(f"  {today}  |  10:00 AM Update")
    print("=" * 60)

    print(f"\n{'OVERVIEW':}")
    print(status_line("Total open slots:", f"{OVERALL['total_open']} across {OVERALL['total_positions']} roles"))
    print(status_line("Hired (confirmed):", f"{OVERALL['hired']} — Jatin Sachdeva (Finance, joins Jun 18)"))
    print(status_line("Active primaries:", str(OVERALL["primary_active"])))
    print(status_line("Backup candidates:", str(OVERALL["backup_active"])))
    print(status_line("Estimated budget:", OVERALL["total_budget"]))

    for pos_id, pos in POSITIONS.items():
        hired_count = len(pos["hired"])
        remaining = pos["target"] - hired_count
        status_flag = "FILLED" if remaining == 0 else ("CRITICAL" if hired_count == 0 else "IN PROGRESS")
        print(f"\n{'─'*60}")
        print(f"  [{pos_id}] {pos['title']}")
        print(f"  Target: {pos['target']}  |  Hired: {hired_count}  |  Still needed: {remaining}  |  {status_flag}")

        if "alert" in pos:
            print(f"  ⚠  {pos['alert']}")

        if pos["hired"]:
            print(f"\n  HIRED:")
            for c in pos["hired"]:
                print(f"    ✓ {c['name']} — {c['ctc']} — Joining: {c['joining']}")

        if pos["primary"]:
            print(f"\n  PRIMARY CANDIDATES:")
            for c in pos["primary"]:
                print(f"    • {c['name']}  (Score {c['score']}/10)")
                print(f"      CTC: {c['ctc']}  |  Notice: {c['notice']}")
                print(f"      Action: {c['action']}")

        if pos["backups"]:
            print(f"\n  BACKUPS: {', '.join(pos['backups'])}")

    print(f"\n{'─'*60}")
    print("  PRIORITY ACTIONS TODAY")
    print("  1. Contact CA Rahul Madaan  → Finance close (rahulmadaan942@gmail.com / 9873060422)")
    print("  2. Contact Kuwarjeet Sidana → DRO close — NO BACKUP (kuwarjeetsingh18@gmail.com / 8800100021)")
    print("  3. Outreach Kamal (RPA #1)  → Via GIST / Hemant Kulasri")
    print("  4. Confirm Jatin Sachdeva   → Onboarding prep for June 18")
    print("=" * 60)


if __name__ == "__main__":
    print_report()
