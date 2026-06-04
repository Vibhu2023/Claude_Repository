#!/usr/bin/env python3
"""
Daily Pipeline Status Report Generator
Run each morning to get a concise snapshot of candidate pipeline status.
"""

from datetime import date, datetime

TODAY = date.today()

CANDIDATES = [
    # Finance
    {
        "id": "FIN-JAT-001", "name": "Jatin Sachdeva", "role": "Sr Finance Manager",
        "status": "HIRED", "score": 7.2,
        "ctc": "₹4.5L", "joining": date(2026, 6, 18),
        "contact": "N/A", "source": "GIST Consulting",
        "notes": "Confirmed. Onboarding June 18.",
    },
    {
        "id": "FIN-RAH-001", "name": "CA Rahul Madaan", "role": "Sr Finance Manager",
        "status": "PRIMARY", "score": 8.8,
        "ctc": "₹42-44L", "joining": None,
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "source": "GIST Consulting",
        "notes": "Only viable Finance option. 30-day notice. Mid-June start.",
    },
    {
        "id": "FIN-MAN-001", "name": "CA Manu Singla", "role": "Sr Finance Manager",
        "status": "BACKUP", "score": 8.9,
        "ctc": "TBD", "joining": None,
        "contact": "N/A", "source": "GIST",
        "notes": "Too junior (3 yrs). Backup only.",
    },
    {
        "id": "FIN-JAT-002", "name": "CA Jatin Anand", "role": "Sr Finance Manager",
        "status": "BACKUP", "score": 8.5,
        "ctc": "TBD", "joining": None,
        "contact": "N/A", "source": "GIST",
        "notes": "6 yrs experience. Backup.",
    },
    {
        "id": "FIN-KAP-001", "name": "CA Kapil Sharma", "role": "Sr Finance Manager",
        "status": "BACKUP", "score": 7.8,
        "ctc": "TBD", "joining": None,
        "contact": "N/A", "source": "GIST",
        "notes": "7 yrs experience. Backup.",
    },
    {
        "id": "FIN-RIT-001", "name": "Ritu Arora", "role": "Sr Finance Manager",
        "status": "BACKUP", "score": 8.2,
        "ctc": "₹31.67L", "joining": None,
        "contact": "N/A", "source": "GIST",
        "notes": "7 yrs. High CTC. Backup.",
    },
    {
        "id": "FIN-SHU-001", "name": "Shukla Satia", "role": "Sr Finance Manager",
        "status": "BACKUP", "score": 7.8,
        "ctc": "TBD", "joining": None,
        "contact": "N/A", "source": "GIST",
        "notes": "6 yrs experience. Backup.",
    },
    # RPA
    {
        "id": "RPA-KAM-001", "name": "Kamal", "role": "RPA Developer",
        "status": "PRIMARY", "score": 7.8,
        "ctc": "₹6.6L", "joining": None,
        "contact": "Via GIST - Hemant Kulasri",
        "source": "GIST Consulting",
        "notes": "UiPath Orchestrator expert. 90-day notice (negotiate to 60). Est. July start.",
    },
    {
        "id": "RPA-ANS-001", "name": "Anshul Vashisth", "role": "RPA Developer",
        "status": "PRIMARY", "score": 8.8,
        "ctc": "₹6L + ₹2-3L training", "joining": None,
        "contact": "From resume",
        "source": "Internal",
        "notes": "SAP FICO integration critical for HANA. Immediate notice. Est. July start.",
    },
    {
        "id": "RPA-SHA-001", "name": "Shahe Faisal", "role": "RPA Developer",
        "status": "OPTIONAL", "score": 8.5,
        "ctc": "₹13-15L", "joining": None,
        "contact": "N/A",
        "source": "PDF May 18",
        "notes": "Premium tier. Capgemini. Competing offers: Cognizant/TCS ₹13L. 15-day notice.",
    },
    {
        "id": "RPA-RIT-001", "name": "Ritik Gupta", "role": "RPA Developer",
        "status": "BACKED OUT", "score": 8.8,
        "ctc": "N/A", "joining": None,
        "contact": "N/A", "source": "N/A",
        "notes": "Was confirmed hired. Withdrew after acceptance.",
    },
    # DRO
    {
        "id": "DRO-KUW-001", "name": "Kuwarjeet Sidana", "role": "Chief Digital Revenue Officer",
        "status": "PRIMARY", "score": 9.5,
        "ctc": "₹28L", "joining": None,
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "source": "GIST Consulting",
        "notes": "ONLY DRO candidate. NO backup. 30-day notice. Est. June 15-30 start.",
    },
]

STATUS_ORDER = ["HIRED", "PRIMARY", "OPTIONAL", "BACKUP", "ON HOLD", "BACKED OUT", "EXCLUDED", "REJECTED", "WITHDRAWN"]
STATUS_EMOJI = {
    "HIRED":      "✅",
    "PRIMARY":    "🔴",
    "OPTIONAL":   "🟡",
    "BACKUP":     "🟢",
    "ON HOLD":    "⏸️",
    "BACKED OUT": "❌",
    "EXCLUDED":   "🚫",
    "REJECTED":   "❌",
    "WITHDRAWN":  "↩️",
}

PRIORITIES = [
    {
        "rank": 1,
        "action": "Confirm Jatin Sachdeva onboarding for June 18",
        "candidate": "Jatin Sachdeva",
        "contact": "N/A",
        "deadline": "NOW",
    },
    {
        "rank": 2,
        "action": "Finalise offer / close with Kuwarjeet Sidana (DRO — no backup)",
        "candidate": "Kuwarjeet Sidana",
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "deadline": "TODAY",
    },
    {
        "rank": 3,
        "action": "Close offer with CA Rahul Madaan (Finance — only primary)",
        "candidate": "CA Rahul Madaan",
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "deadline": "TODAY",
    },
    {
        "rank": 4,
        "action": "Follow up on Kamal (RPA #1) via GIST — negotiate notice from 90→60 days",
        "candidate": "Kamal",
        "contact": "Via GIST - Hemant Kulasri",
        "deadline": "THIS WEEK",
    },
    {
        "rank": 5,
        "action": "Send offer to Anshul Vashisth (RPA #2) + approve ₹2-3L SAP training budget",
        "candidate": "Anshul Vashisth",
        "contact": "From resume",
        "deadline": "THIS WEEK",
    },
]


def days_until(d: date) -> int:
    return (d - TODAY).days


def print_header():
    print("=" * 70)
    print(f"  MOOLCHAND HEALTHCARE — DAILY PIPELINE STATUS")
    print(f"  {TODAY.strftime('%A, %B %d, %Y')}  |  Generated: {datetime.now().strftime('%H:%M')}")
    print("=" * 70)


def print_executive_summary():
    counts = {}
    for c in CANDIDATES:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    hired = counts.get("HIRED", 0)
    primary = counts.get("PRIMARY", 0)
    backup = counts.get("BACKUP", 0)
    closed = sum(counts.get(s, 0) for s in ["REJECTED", "WITHDRAWN", "EXCLUDED", "BACKED OUT"])
    open_positions = 5  # 2 Finance, 2 RPA, 1 DRO

    print("\n📊 EXECUTIVE SUMMARY")
    print("-" * 40)
    print(f"  Open positions  : {open_positions}")
    print(f"  Hired           : {hired}")
    print(f"  Still needed    : {open_positions - hired}")
    print(f"  Active (Primary): {primary}")
    print(f"  Backup pool     : {backup}")
    print(f"  Closed (no hire): {closed}")

    jatin_joining = date(2026, 6, 18)
    days = days_until(jatin_joining)
    print(f"\n  ⏰ Jatin Sachdeva joining in {days} day{'s' if days != 1 else ''} ({jatin_joining})")


def print_priorities():
    print("\n🚨 TODAY'S PRIORITIES")
    print("-" * 40)
    for p in PRIORITIES:
        print(f"  [{p['rank']}] {p['deadline']:10}  {p['action']}")
        if p["contact"] != "N/A":
            print(f"            Contact: {p['contact']}")


def print_pipeline_by_role():
    roles = {}
    for c in CANDIDATES:
        roles.setdefault(c["role"], []).append(c)

    print("\n📋 PIPELINE BY ROLE")
    print("-" * 40)
    for role, candidates in roles.items():
        hired = [c for c in candidates if c["status"] == "HIRED"]
        primary = [c for c in candidates if c["status"] == "PRIMARY"]
        backup = [c for c in candidates if c["status"] == "BACKUP"]

        print(f"\n  {role}")
        for c in sorted(candidates, key=lambda x: STATUS_ORDER.index(x["status"]) if x["status"] in STATUS_ORDER else 99):
            emoji = STATUS_EMOJI.get(c["status"], "•")
            joining_str = ""
            if c["joining"]:
                d = days_until(c["joining"])
                joining_str = f"  (joins in {d}d)"
            print(f"    {emoji} {c['name']:25} {c['status']:12} {c['score']}/10{joining_str}")
            if c["status"] in ("PRIMARY", "HIRED") and c["notes"]:
                print(f"       ↳ {c['notes']}")


def print_risk_flags():
    print("\n⚠️  RISK FLAGS")
    print("-" * 40)
    print("  🔴 CRITICAL  DRO has NO backup — must close Kuwarjeet this week")
    print("  🔴 HIGH      RPA at 0/2 hired — Ritik backed out after acceptance")
    print("  🟡 MEDIUM    Shahe Faisal (RPA premium) competing offers at ₹13L")
    print("  🟡 MEDIUM    Finance: Rahul is only primary; backups less qualified")
    print("  🟢 LOW       Jatin Sachdeva onboarding on track for June 18")


def print_footer():
    print("\n" + "=" * 70)
    print("  Run `python daily_pipeline_status.py` each morning for a fresh snapshot.")
    print("  Full report: HIRING_PIPELINE_REPORT.md")
    print("=" * 70 + "\n")


def main():
    print_header()
    print_executive_summary()
    print_priorities()
    print_pipeline_by_role()
    print_risk_flags()
    print_footer()


if __name__ == "__main__":
    main()
