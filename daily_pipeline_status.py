#!/usr/bin/env python3
"""Daily 10 AM pipeline status report for Moolchand Healthcare Group hiring."""

from datetime import date, timedelta

TODAY = date.today()

# --------------------------------------------------------------------------- #
# Candidate data — update statuses here as the pipeline progresses
# --------------------------------------------------------------------------- #

POSITIONS = {
    "FIN-001": {
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired_count": 1,
    },
    "RPA-001": {
        "title": "RPA Developer",
        "target": 2,
        "hired_count": 0,
    },
    "DRO-001": {
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired_count": 0,
    },
}

CANDIDATES = [
    # ---- Finance (FIN-001) ----
    {
        "id": "FIN-JAT-001",
        "name": "Jatin Sachdeva",
        "position": "FIN-001",
        "status": "HIRED",
        "score": 7.2,
        "ctc": "₹4.5L",
        "joining_date": date(2026, 6, 18),
        "contact": None,
        "notice_days": 0,
        "notes": "Confirmed hire. Onboarding June 18.",
    },
    {
        "id": "FIN-RAH-001",
        "name": "CA Rahul Madaan",
        "position": "FIN-001",
        "status": "PRIMARY",
        "score": 8.8,
        "ctc": "₹42-44L",
        "joining_date": None,
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "notice_days": 30,
        "notes": "Best finance candidate. Contact immediately — only viable primary.",
    },
    {
        "id": "FIN-MAN-001",
        "name": "CA Manu Singla",
        "position": "FIN-001",
        "status": "BACKUP",
        "score": 8.9,
        "ctc": "TBD",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "Too junior (3 yrs). Activate if Rahul unavailable.",
    },
    {
        "id": "FIN-JAT-002",
        "name": "CA Jatin Anand",
        "position": "FIN-001",
        "status": "BACKUP",
        "score": 8.5,
        "ctc": "TBD",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "6 years experience. Viable backup.",
    },
    {
        "id": "FIN-KAP-001",
        "name": "CA Kapil Sharma",
        "position": "FIN-001",
        "status": "BACKUP",
        "score": 7.8,
        "ctc": "TBD",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "7 years experience.",
    },
    {
        "id": "FIN-RIT-001",
        "name": "Ritu Arora",
        "position": "FIN-001",
        "status": "BACKUP",
        "score": 8.2,
        "ctc": "₹31.67L",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "7 years. High CTC — budget approval needed.",
    },
    {
        "id": "FIN-SHU-001",
        "name": "Shukla Satia",
        "position": "FIN-001",
        "status": "BACKUP",
        "score": 7.8,
        "ctc": "TBD",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "6 years experience.",
    },
    # ---- RPA (RPA-001) ----
    {
        "id": "RPA-RIT-001",
        "name": "Ritik Gupta",
        "position": "RPA-001",
        "status": "BACKED_OUT",
        "score": 8.8,
        "ctc": "TBD",
        "joining_date": None,
        "contact": None,
        "notice_days": None,
        "notes": "Was confirmed; withdrew after offer acceptance.",
    },
    {
        "id": "RPA-KAM-001",
        "name": "Kamal",
        "position": "RPA-001",
        "status": "PRIMARY",
        "score": 7.8,
        "ctc": "₹6.6L",
        "joining_date": date(2026, 7, 1),
        "contact": "Via GIST — Hemant Kulasri",
        "notice_days": 90,
        "notes": "Negotiate notice from 90→60 days. UiPath Orchestrator expert.",
    },
    {
        "id": "RPA-ANS-001",
        "name": "Anshul Vashisth",
        "position": "RPA-001",
        "status": "PRIMARY",
        "score": 8.8,
        "ctc": "₹6L + ₹2-3L training",
        "joining_date": date(2026, 7, 1),
        "contact": "From resume (internal)",
        "notice_days": 0,
        "notes": "SAP FICO integration — critical for HANA. Immediate joiner.",
    },
    {
        "id": "RPA-SHA-001",
        "name": "Shahe Faisal",
        "position": "RPA-001",
        "status": "OPTIONAL",
        "score": 8.5,
        "ctc": "₹13-15L",
        "joining_date": None,
        "contact": "PDF (May 18)",
        "notice_days": 15,
        "notes": "Premium tier. Competing offers from Cognizant/TCS at ₹13L.",
    },
    # ---- DRO (DRO-001) ----
    {
        "id": "DRO-KUW-001",
        "name": "Kuwarjeet Sidana",
        "position": "DRO-001",
        "status": "PRIMARY",
        "score": 9.5,
        "ctc": "₹28L",
        "joining_date": date(2026, 6, 30),
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "notice_days": 30,
        "notes": "Only candidate — NO backup. Close urgently. Score 9.5/10.",
    },
]

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🔵",
    "BACKUP": "🟡",
    "OPTIONAL": "🟠",
    "ON_HOLD": "⏸️",
    "BACKED_OUT": "❌",
    "REJECTED": "🚫",
    "WITHDRAWN": "↩️",
    "EXCLUDED": "⛔",
}

# --------------------------------------------------------------------------- #
# Report generation
# --------------------------------------------------------------------------- #

def urgency_flags(candidate: dict) -> list[str]:
    flags = []
    s = candidate["status"]
    if s == "PRIMARY" and candidate["joining_date"]:
        days_to_join = (candidate["joining_date"] - TODAY).days
        if days_to_join < 0:
            flags.append(f"⚠️  OVERDUE — expected start was {candidate['joining_date']}")
        elif days_to_join <= 7:
            flags.append(f"🔴 START IN {days_to_join} DAY(S) — {candidate['joining_date']}")
        elif days_to_join <= 14:
            flags.append(f"🟠 Start in {days_to_join} days — {candidate['joining_date']}")
    if s == "HIRED" and candidate["joining_date"]:
        days_since = (TODAY - candidate["joining_date"]).days
        if days_since >= 0:
            flags.append(f"🏢 JOINED {days_since} day(s) ago ({candidate['joining_date']})")
    return flags


def action_today(candidate: dict) -> str | None:
    s = candidate["status"]
    if s == "PRIMARY":
        if candidate["contact"]:
            return f"Contact: {candidate['contact']}"
        return "Follow up — no contact info on record"
    return None


def build_report() -> str:
    lines = []

    lines.append(f"# Moolchand Healthcare Group — Daily Pipeline Status")
    lines.append(f"**Report Date:** {TODAY.strftime('%B %d, %Y')}  ")
    lines.append(f"**Generated:** 10:00 AM IST  ")
    lines.append(f"**Hiring Manager:** Vibhu Talwar")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive summary
    hired = [c for c in CANDIDATES if c["status"] == "HIRED"]
    primaries = [c for c in CANDIDATES if c["status"] == "PRIMARY"]
    backups = [c for c in CANDIDATES if c["status"] == "BACKUP"]
    backed_out = [c for c in CANDIDATES if c["status"] == "BACKED_OUT"]

    total_target = sum(p["target"] for p in POSITIONS.values())
    total_hired = len(hired)
    still_needed = total_target - total_hired

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Open Positions | {len(POSITIONS)} |")
    lines.append(f"| Total Seats | {total_target} |")
    lines.append(f"| Hired | {total_hired} |")
    lines.append(f"| Still Needed | {still_needed} |")
    lines.append(f"| Active Primaries | {len(primaries)} |")
    lines.append(f"| Backups Available | {len(backups)} |")
    lines.append(f"| Backed Out | {len(backed_out)} |")
    lines.append("")

    # Overdue / urgent flags
    urgent = []
    for c in CANDIDATES:
        flags = urgency_flags(c)
        if flags:
            for f in flags:
                urgent.append(f"- **{c['name']}** ({c['id']}): {f}")

    if urgent:
        lines.append("## 🚨 Alerts & Deadlines")
        lines.append("")
        lines.extend(urgent)
        lines.append("")

    # Today's actions
    actions = [
        (c, action_today(c)) for c in CANDIDATES if action_today(c)
    ]
    if actions:
        lines.append("## ⚡ Today's Required Actions")
        lines.append("")
        for c, act in actions:
            lines.append(f"- **{c['name']}** ({c['id']}) — {c['position']} | Score: {c['score']}/10")
            lines.append(f"  - {act}")
            lines.append(f"  - CTC: {c['ctc']} | Note: {c['notes']}")
        lines.append("")

    # Per-position breakdown
    lines.append("---")
    lines.append("")
    lines.append("## Position Breakdown")
    lines.append("")

    for pos_id, pos in POSITIONS.items():
        pos_candidates = [c for c in CANDIDATES if c["position"] == pos_id]
        pos_hired = [c for c in pos_candidates if c["status"] == "HIRED"]
        still_open = pos["target"] - len(pos_hired)

        status_icon = "✅" if still_open == 0 else ("🔴" if still_open > 0 else "✅")
        lines.append(f"### {status_icon} {pos_id} — {pos['title']}")
        lines.append(f"**Seats:** {pos['target']} target | **Hired:** {len(pos_hired)} | **Remaining:** {still_open}")
        lines.append("")

        for c in pos_candidates:
            emoji = STATUS_EMOJI.get(c["status"], "•")
            join_str = f" | Join: {c['joining_date']}" if c["joining_date"] else ""
            lines.append(f"| {emoji} | **{c['name']}** ({c['id']}) | {c['status']} | Score: {c['score']}/10 | CTC: {c['ctc']}{join_str} |")
            for flag in urgency_flags(c):
                lines.append(f"|   |   | {flag} |   |   |")

        lines.append("")

    # Upcoming milestones
    milestones = []
    for c in CANDIDATES:
        if c["joining_date"] and c["status"] in ("HIRED", "PRIMARY"):
            days = (c["joining_date"] - TODAY).days
            milestones.append((c["joining_date"], c["name"], c["status"], days))

    milestones.sort()
    if milestones:
        lines.append("---")
        lines.append("")
        lines.append("## Upcoming Milestones")
        lines.append("")
        lines.append("| Date | Candidate | Status | Days Away |")
        lines.append("|------|-----------|--------|-----------|")
        for jd, name, st, days in milestones:
            day_str = "TODAY" if days == 0 else (f"{days}d away" if days > 0 else f"{abs(days)}d ago")
            lines.append(f"| {jd} | {name} | {st} | {day_str} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"**Last Updated:** {TODAY}  ")
    lines.append(f"**Next Report:** {TODAY + timedelta(days=1)} at 10:00 AM")

    return "\n".join(lines)


def main() -> None:
    report = build_report()
    print(report)

    # Overwrite the daily status file
    output_path = "DAILY_PIPELINE_STATUS.md"
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\n[Saved → {output_path}]")


if __name__ == "__main__":
    main()
