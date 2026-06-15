"""
Daily pipeline status generator for Moolchand Healthcare Group hiring pipeline.
Reads HIRING_PIPELINE_REPORT.md and produces a dated status snapshot in
DAILY_PIPELINE_STATUS.md with urgency flags based on the current date.
"""

from datetime import date, timedelta
import os

TODAY = date.today()
REPORT_FILE = "HIRING_PIPELINE_REPORT.md"
OUTPUT_FILE = "DAILY_PIPELINE_STATUS.md"


def days_until(target: date) -> int:
    return (target - TODAY).days


def urgency_label(days: int) -> str:
    if days < 0:
        return f"⚠️ OVERDUE by {abs(days)} days"
    if days == 0:
        return "🔴 TODAY"
    if days <= 3:
        return f"🔴 IN {days} DAY{'S' if days > 1 else ''}"
    if days <= 7:
        return f"🟠 IN {days} DAYS"
    return f"🟢 IN {days} DAYS"


def build_status_report() -> str:
    # Key milestone dates
    jatin_join = date(2026, 6, 18)
    kuwarjeet_start_window_end = date(2026, 6, 30)
    kamal_start = date(2026, 7, 1)
    anshul_start = date(2026, 7, 1)

    # Candidate data (sourced from HIRING_PIPELINE_REPORT.md, May 19 2026)
    candidates = [
        {
            "position": "Sr Finance Manager (FIN-001)",
            "name": "Jatin Sachdeva",
            "id": "FIN-JAT-001",
            "status": "HIRED ✅",
            "score": 7.2,
            "offer": "₹4.5L",
            "start_date": jatin_join,
            "note": "Onboarding prep — joins in " + urgency_label(days_until(jatin_join)),
            "action_required": days_until(jatin_join) <= 7,
        },
        {
            "position": "Sr Finance Manager (FIN-001)",
            "name": "CA Rahul Madaan",
            "id": "FIN-RAH-001",
            "status": "PRIMARY",
            "score": 8.8,
            "offer": "₹42–44L",
            "start_date": date(2026, 6, 20),
            "note": "ONLY viable Finance candidate — confirm offer status",
            "action_required": True,
        },
        {
            "position": "RPA Developer (RPA-001) — Slot 1",
            "name": "Kamal",
            "id": "RPA-KAM-001",
            "status": "PRIMARY",
            "score": 7.8,
            "offer": "₹6.6L",
            "start_date": kamal_start,
            "note": "Contact via GIST (Hemant Kulasri) — negotiate 90→60-day notice",
            "action_required": days_until(kamal_start) <= 30,
        },
        {
            "position": "RPA Developer (RPA-001) — Slot 2",
            "name": "Anshul Vashisth",
            "id": "RPA-ANS-001",
            "status": "PRIMARY",
            "score": 8.8,
            "offer": "₹6L + ₹2–3L SAP training",
            "start_date": anshul_start,
            "note": "SAP FICO integration strength — approve training budget",
            "action_required": days_until(anshul_start) <= 30,
        },
        {
            "position": "Chief Digital Revenue Officer (DRO-001)",
            "name": "Kuwarjeet Sidana",
            "id": "DRO-KUW-001",
            "status": "PRIMARY — NO BACKUP",
            "score": 9.5,
            "offer": "₹28L",
            "start_date": kuwarjeet_start_window_end,
            "note": "Est. start June 15–30 — confirm interview/offer outcome CRITICAL",
            "action_required": True,
        },
    ]

    # Backup Finance candidates
    backups = [
        ("CA Manu Singla",   "FIN-MAN-001", 8.9, "Too junior (3 yrs) — use only if Rahul declines"),
        ("CA Jatin Anand",   "FIN-JAT-002", 8.5, "6 yrs experience"),
        ("CA Kapil Sharma",  "FIN-KAP-001", 7.8, "7 yrs experience"),
        ("Ritu Arora",       "FIN-RIT-001", 8.2, "7 yrs, high CTC ₹31.67L"),
        ("Shukla Satia",     "FIN-SHU-001", 7.8, "6 yrs experience"),
    ]

    lines = [
        f"# Moolchand Healthcare Group — Daily Pipeline Status",
        f"**Date:** {TODAY.strftime('%B %d, %Y')} | **Hiring Manager:** Vibhu Talwar",
        f"**Report Source:** HIRING_PIPELINE_REPORT.md (baseline May 19, 2026)",
        "",
        "---",
        "",
        "## Pipeline Snapshot",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        "| Open Positions | 3 |",
        "| Total Candidates Tracked | 27 |",
        "| Hired | 1 (Jatin Sachdeva — Finance) |",
        "| Active Primary Candidates | 4 |",
        "| Backup Candidates | 5 (Finance) |",
        "| Budget Committed | ₹4.5L |",
        "| Budget Remaining (est.) | ₹89–91L |",
        "",
        "---",
        "",
        "## Candidate Status by Position",
        "",
    ]

    action_items = []

    for c in candidates:
        days = days_until(c["start_date"])
        urgency = urgency_label(days)
        lines += [
            f"### {c['position']}",
            f"**{c['name']}** (`{c['id']}`) — Status: **{c['status']}** | Score: {c['score']}/10",
            f"- Offer: {c['offer']}",
            f"- Target Start: {c['start_date'].strftime('%B %d, %Y')} — {urgency}",
            f"- Note: {c['note']}",
            "",
        ]
        if c["action_required"]:
            action_items.append(f"- **{c['name']}** ({c['id']}): {c['note']}")

    lines += [
        "---",
        "",
        "## Finance Backup Bench (if Rahul Madaan declines)",
        "",
        "| Name | ID | Score | Note |",
        "|------|----|-------|------|",
    ]
    for name, cid, score, note in backups:
        lines.append(f"| {name} | {cid} | {score}/10 | {note} |")

    lines += [
        "",
        "---",
        "",
        "## ⚡ Action Items for Today",
        "",
    ]
    if action_items:
        lines += action_items
    else:
        lines.append("- No critical actions flagged for today.")

    lines += [
        "",
        "---",
        "",
        "## Risk Flags",
        "",
        "| Risk | Severity | Mitigation |",
        "|------|----------|------------|",
        "| Rahul Madaan declines Finance offer | HIGH | 5 backup candidates available |",
        "| RPA market competition (Kamal/Anshul) | MEDIUM | Fast-track offers; Shahe Faisal premium fallback |",
        "| DRO — Kuwarjeet is sole candidate | CRITICAL | Must close this week; no fallback exists |",
        "| Timeline compression (June 18 join) | HIGH | Parallel outreach; onboarding prep now |",
        "",
        "---",
        "",
        f"*Auto-generated daily at 10:00 AM IST · {TODAY.isoformat()}*",
    ]

    return "\n".join(lines) + "\n"


def main():
    report = build_status_report()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[pipeline_daily_update] Status report written to {OUTPUT_FILE} ({TODAY})")


if __name__ == "__main__":
    main()
