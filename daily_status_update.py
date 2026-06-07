"""
Daily candidate pipeline status updater.
Reads HIRING_PIPELINE_REPORT.md and writes a dated DAILY_STATUS.md snapshot.
Run via GitHub Actions every day at 10 AM IST.
"""

import re
import sys
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
REPORT_FILE = "HIRING_PIPELINE_REPORT.md"
OUTPUT_FILE = "DAILY_STATUS.md"

POSITION_TARGETS = {
    "FIN-001": {"title": "Sr Finance Manager / Finance & AR Lead", "target": 2},
    "RPA-001": {"title": "RPA Developer", "target": 2},
    "DRO-001": {"title": "Chief Digital Revenue Officer", "target": 1},
}

# Static candidate data extracted from HIRING_PIPELINE_REPORT.md.
# Update this list whenever a candidate's status changes in the main report.
CANDIDATES = [
    # Finance
    {"id": "FIN-JAT-001", "name": "Jatin Sachdeva",      "position": "FIN-001", "score": 7.2, "status": "Hired",      "offer": "₹4.5L",   "joining": "June 18, 2026", "note": "CONFIRMED"},
    {"id": "FIN-RAH-001", "name": "CA Rahul Madaan",     "position": "FIN-001", "score": 8.8, "status": "Primary",    "offer": "₹42-44L", "joining": "Mid-June",      "note": "Contact TODAY — only viable option"},
    {"id": "FIN-MAN-001", "name": "CA Manu Singla",      "position": "FIN-001", "score": 8.9, "status": "Backup",     "offer": "—",       "joining": "—",             "note": "Too junior (3 yrs)"},
    {"id": "FIN-JAT-002", "name": "CA Jatin Anand",      "position": "FIN-001", "score": 8.5, "status": "Backup",     "offer": "—",       "joining": "—",             "note": "6 yrs experience"},
    {"id": "FIN-KAP-001", "name": "CA Kapil Sharma",     "position": "FIN-001", "score": 7.8, "status": "Backup",     "offer": "—",       "joining": "—",             "note": "7 yrs experience"},
    {"id": "FIN-RIT-001", "name": "Ritu Arora",          "position": "FIN-001", "score": 8.2, "status": "Backup",     "offer": "—",       "joining": "—",             "note": "High CTC ₹31.67L"},
    {"id": "FIN-SHU-001", "name": "Shukla Satia",        "position": "FIN-001", "score": 7.8, "status": "Backup",     "offer": "—",       "joining": "—",             "note": "6 yrs experience"},
    {"id": "FIN-ABH-001", "name": "CA Abhishek Goyal",   "position": "FIN-001", "score": 9.3, "status": "Rejected",   "offer": "—",       "joining": "—",             "note": "Declined offer"},
    {"id": "FIN-VIK-001", "name": "Vikas Jain",          "position": "FIN-001", "score": 7.5, "status": "Rejected",   "offer": "—",       "joining": "—",             "note": "Rejected — SAP gap"},
    # RPA
    {"id": "RPA-RIT-001", "name": "Ritik Gupta",         "position": "RPA-001", "score": 8.8, "status": "Backed Out", "offer": "—",       "joining": "—",             "note": "Withdrew after acceptance"},
    {"id": "RPA-KAM-001", "name": "Kamal",               "position": "RPA-001", "score": 7.8, "status": "Primary",    "offer": "₹6.6L",   "joining": "July 2026",     "note": "Contact via GIST (Hemant Kulasri)"},
    {"id": "RPA-ANS-001", "name": "Anshul Vashisth",     "position": "RPA-001", "score": 8.8, "status": "Primary",    "offer": "₹6L+trng","joining": "July 2026",     "note": "SAP FICO advantage — contact Week 2"},
    {"id": "RPA-SHA-001", "name": "Shahe Faisal",        "position": "RPA-001", "score": 8.5, "status": "Optional",   "offer": "₹13-15L", "joining": "15 days",       "note": "Premium tier — needs budget approval"},
    {"id": "RPA-SUB-001", "name": "Subrat",              "position": "RPA-001", "score": 0.0, "status": "Excluded",   "offer": "—",       "joining": "—",             "note": "Limited enterprise experience"},
    {"id": "RPA-JAS-001", "name": "Jasmin Bar",          "position": "RPA-001", "score": 0.0, "status": "Excluded",   "offer": "—",       "joining": "—",             "note": "Limited enterprise experience"},
    {"id": "RPA-HAR-001", "name": "Hardik Agarwal",      "position": "RPA-001", "score": 0.0, "status": "Rejected",   "offer": "—",       "joining": "—",             "note": "Junior — mentorship only"},
    # DRO
    {"id": "DRO-KUW-001", "name": "Kuwarjeet Sidana",    "position": "DRO-001", "score": 9.5, "status": "Primary",    "offer": "₹28L",    "joining": "June 15-30",    "note": "ONLY candidate — must close this week"},
]

STATUS_EMOJI = {
    "Hired":      "✅",
    "Primary":    "🔵",
    "Backup":     "🟡",
    "Optional":   "🟠",
    "On Hold":    "⏸️",
    "Excluded":   "🚫",
    "Rejected":   "❌",
    "Withdrawn":  "↩️",
    "Backed Out": "⚠️",
}

PRIORITY_ACTIONS = [
    ("TODAY", "🔴", "CA Rahul Madaan (Finance)", "rahulmadaan942@gmail.com", "9873060422", "Offer ₹42-44L — only viable Finance option"),
    ("TODAY", "🔴", "Kuwarjeet Sidana (DRO)",    "kuwarjeetsingh18@gmail.com", "8800100021", "Offer ₹28L — no backup, must close now"),
    ("THIS WEEK", "🟠", "Kamal (RPA #1)", "Via GIST — Hemant Kulasri", "", "Offer ₹6.6L, negotiate notice 90→60 days"),
    ("WEEK 2",    "🟡", "Anshul Vashisth (RPA #2)", "From resume", "", "Offer ₹6L + ₹2-3L SAP training budget"),
    ("ONGOING",   "🟢", "Jatin Sachdeva (Finance)", "Already hired", "", "Confirm onboarding & June 18 first-day logistics"),
]


def build_position_summary():
    rows = []
    for pos_id, pos in POSITION_TARGETS.items():
        hired   = sum(1 for c in CANDIDATES if c["position"] == pos_id and c["status"] == "Hired")
        primary = sum(1 for c in CANDIDATES if c["position"] == pos_id and c["status"] == "Primary")
        backup  = sum(1 for c in CANDIDATES if c["position"] == pos_id and c["status"] == "Backup")
        needed  = pos["target"] - hired
        urgency = "🔴 CRITICAL" if needed > 0 and primary == 0 else ("🟠 URGENT" if needed > 0 else "✅ FILLED")
        rows.append(f"| {pos['title']} | {pos['target']} | {hired} | {needed} | {primary} | {backup} | {urgency} |")
    return rows


def build_active_candidates_table():
    active_statuses = {"Hired", "Primary", "Backup", "Optional"}
    rows = []
    for c in CANDIDATES:
        if c["status"] not in active_statuses:
            continue
        emoji = STATUS_EMOJI.get(c["status"], "")
        score_str = f"{c['score']:.1f}" if c["score"] > 0 else "—"
        rows.append(
            f"| {c['id']} | {c['name']} | {emoji} {c['status']} | "
            f"{score_str} | {c['offer']} | {c['joining']} | {c['note']} |"
        )
    return rows


def count_by_status():
    from collections import Counter
    counts = Counter(c["status"] for c in CANDIDATES)
    return counts


def generate_report(today: datetime) -> str:
    date_str  = today.strftime("%B %d, %Y")
    time_str  = today.strftime("%I:%M %p IST")
    counts    = count_by_status()
    pos_rows  = build_position_summary()
    cand_rows = build_active_candidates_table()

    total_active = counts.get("Hired", 0) + counts.get("Primary", 0) + counts.get("Backup", 0)

    lines = [
        f"# Daily Candidate Pipeline Status",
        f"**Date:** {date_str} | **Generated:** {time_str}  ",
        f"**Hiring Manager:** Vibhu Talwar | **Moolchand Healthcare Group**",
        "",
        "---",
        "",
        "## Pipeline Snapshot",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Candidates | {len(CANDIDATES)} |",
        f"| Hired | {counts.get('Hired', 0)} |",
        f"| Primary (Active) | {counts.get('Primary', 0)} |",
        f"| Backup | {counts.get('Backup', 0)} |",
        f"| Optional | {counts.get('Optional', 0)} |",
        f"| On Hold | {counts.get('On Hold', 0)} |",
        f"| Rejected / Excluded | {counts.get('Rejected', 0) + counts.get('Excluded', 0)} |",
        f"| Withdrawn / Backed Out | {counts.get('Withdrawn', 0) + counts.get('Backed Out', 0)} |",
        "",
        "---",
        "",
        "## Position Fill Status",
        "",
        "| Position | Target | Hired | Still Needed | Primaries | Backups | Urgency |",
        "|----------|--------|-------|--------------|-----------|---------|---------|",
        *pos_rows,
        "",
        "---",
        "",
        "## Active Candidates",
        "",
        "| ID | Name | Status | Score | Offer | Est. Start | Notes |",
        "|----|------|--------|-------|-------|------------|-------|",
        *cand_rows,
        "",
        "---",
        "",
        "## Priority Actions",
        "",
    ]

    for timeline, emoji, name, contact, phone, reason in PRIORITY_ACTIONS:
        contact_str = f"{contact}" + (f" | {phone}" if phone else "")
        lines += [
            f"### {emoji} {timeline}: {name}",
            f"- **Contact:** {contact_str}",
            f"- **Action:** {reason}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Key Risks (Today)",
        "",
        "| Risk | Impact | Status |",
        "|------|--------|--------|",
        "| Rahul Madaan unavailable (Finance) | High | Low likelihood — best candidate |",
        "| RPA market competition (Kamal / Anshul) | High | Medium — fast-track contact needed |",
        "| DRO no backup (Kuwarjeet) | CRITICAL | Medium-High — must close this week |",
        "| Timeline pressure (Jatin joins June 18) | High | High — onboarding prep now |",
        "",
        "---",
        "",
        "## Cost Tracker",
        "",
        "| Hire | CTC | Status |",
        "|------|-----|--------|",
        "| Jatin Sachdeva (Finance) | ₹4.5L | ✅ HIRED |",
        "| CA Rahul Madaan (Finance) | ₹42-44L | Offer pending |",
        "| Kamal (RPA #1) | ₹6.6L | Outreach pending |",
        "| Anshul Vashisth (RPA #2) | ₹6L + ₹2-3L training | Week 2 outreach |",
        "| Kuwarjeet Sidana (DRO) | ₹28L | Offer pending |",
        "| **TOTAL COMMITTED** | **₹4.5L** | |",
        "| **TOTAL ESTIMATED** | **₹89-91L** | |",
        "",
        "---",
        "",
        f"*Auto-generated daily at 10:00 AM IST. "
        f"Source of truth: [HIRING_PIPELINE_REPORT.md](HIRING_PIPELINE_REPORT.md)*",
    ]

    return "\n".join(lines) + "\n"


def main():
    now = datetime.now(IST)
    report = generate_report(now)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[{now.strftime('%Y-%m-%d %H:%M IST')}] DAILY_STATUS.md updated.")


if __name__ == "__main__":
    main()
