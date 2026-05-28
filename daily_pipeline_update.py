#!/usr/bin/env python3
"""Daily hiring pipeline status update generator for Moolchand Healthcare Group."""

from datetime import date, timedelta

TODAY = date.today()

POSITIONS = {
    "FIN-001": {
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": 1,
    },
    "RPA-001": {
        "title": "RPA Developer",
        "target": 2,
        "hired": 0,
    },
    "DRO-001": {
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": 0,
    },
}

CANDIDATES = [
    # Finance
    {
        "id": "FIN-JAT-001", "name": "Jatin Sachdeva", "position": "FIN-001",
        "status": "HIRED", "score": 7.2,
        "offer": "₹4.5L", "joining": date(2026, 6, 18),
        "action": "Confirm onboarding details",
        "priority": 5,
    },
    {
        "id": "FIN-RAH-001", "name": "CA Rahul Madaan", "position": "FIN-001",
        "status": "PRIMARY", "score": 8.8,
        "offer": "₹42-44L", "notice_days": 30,
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "action": "CONTACT IMMEDIATELY — only viable Finance option",
        "priority": 1,
    },
    {
        "id": "FIN-MAN-001", "name": "CA Manu Singla", "position": "FIN-001",
        "status": "BACKUP", "score": 8.9,
        "action": "Activate if Rahul unavailable",
        "priority": None,
    },
    {
        "id": "FIN-JAT-002", "name": "CA Jatin Anand", "position": "FIN-001",
        "status": "BACKUP", "score": 8.5,
        "action": "Backup option",
        "priority": None,
    },
    {
        "id": "FIN-KAP-001", "name": "CA Kapil Sharma", "position": "FIN-001",
        "status": "BACKUP", "score": 7.8,
        "action": "Backup option",
        "priority": None,
    },
    {
        "id": "FIN-RIT-001", "name": "Ritu Arora", "position": "FIN-001",
        "status": "BACKUP", "score": 8.2,
        "action": "Backup option (high CTC ₹31.67L)",
        "priority": None,
    },
    {
        "id": "FIN-SHU-001", "name": "Shukla Satia", "position": "FIN-001",
        "status": "BACKUP", "score": 7.8,
        "action": "Backup option",
        "priority": None,
    },
    {
        "id": "FIN-ABH-001", "name": "CA Abhishek Goyal", "position": "FIN-001",
        "status": "REJECTED", "score": 9.3,
        "action": "Declined offer",
        "priority": None,
    },
    {
        "id": "FIN-VIK-001", "name": "Vikas Jain", "position": "FIN-001",
        "status": "REJECTED", "score": 7.5,
        "action": "Rejected by Moolchand — SAP gap",
        "priority": None,
    },
    # RPA
    {
        "id": "RPA-KAM-001", "name": "Kamal", "position": "RPA-001",
        "status": "PRIMARY", "score": 7.8,
        "offer": "₹6.6L", "notice_days": 90,
        "contact": "Via GIST — Hemant Kulasri",
        "action": "CONTACT THIS WEEK — UiPath Orchestrator expert",
        "priority": 3,
    },
    {
        "id": "RPA-ANS-001", "name": "Anshul Vashisth", "position": "RPA-001",
        "status": "PRIMARY", "score": 8.8,
        "offer": "₹6L + ₹2-3L SAP training",
        "contact": "From resume",
        "action": "CONTACT WEEK 2 — SAP FICO integration advantage",
        "priority": 4,
    },
    {
        "id": "RPA-SHA-001", "name": "Shahe Faisal", "position": "RPA-001",
        "status": "OPTIONAL", "score": 8.5,
        "offer": "₹13-15L (premium budget required)",
        "contact": "From PDF (May 18)",
        "action": "OPTIONAL — approve budget first (Cognizant ₹13L counter-offer)",
        "priority": None,
    },
    {
        "id": "RPA-RIT-001", "name": "Ritik Gupta", "position": "RPA-001",
        "status": "BACKED_OUT", "score": 8.8,
        "action": "Was hired; withdrew after acceptance",
        "priority": None,
    },
    {
        "id": "RPA-SUB-001", "name": "Subrat", "position": "RPA-001",
        "status": "EXCLUDED", "score": None,
        "action": "Do not contact — limited enterprise exp.",
        "priority": None,
    },
    {
        "id": "RPA-JAS-001", "name": "Jasmin Bar", "position": "RPA-001",
        "status": "EXCLUDED", "score": None,
        "action": "Do not contact — limited enterprise exp.",
        "priority": None,
    },
    {
        "id": "RPA-HAR-001", "name": "Hardik Agarwal", "position": "RPA-001",
        "status": "EXCLUDED", "score": None,
        "action": "Junior — mentorship-pair only",
        "priority": None,
    },
    # DRO
    {
        "id": "DRO-KUW-001", "name": "Kuwarjeet Sidana", "position": "DRO-001",
        "status": "PRIMARY", "score": 9.5,
        "offer": "₹28L", "notice_days": 30,
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "joining": date(2026, 6, 15),
        "action": "INTERVIEW THIS WEEK — only DRO candidate, no backup",
        "priority": 2,
    },
]

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🔥",
    "BACKUP": "🔄",
    "OPTIONAL": "💡",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}


def days_label(d: date) -> str:
    delta = (d - TODAY).days
    if delta == 0:
        return "**TODAY**"
    if delta > 0:
        return f"in {delta} day{'s' if delta != 1 else ''}"
    return f"{-delta} day{'s' if -delta != 1 else ''} ago"


def count_by_status(candidates):
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return counts


def positions_filled():
    filled = sum(p["hired"] for p in POSITIONS.values())
    needed = sum(p["target"] for p in POSITIONS.values())
    return filled, needed


def generate_report() -> str:
    lines = []
    filled, needed = positions_filled()
    counts = count_by_status(CANDIDATES)
    primary_count = counts.get("PRIMARY", 0)
    hired_count = counts.get("HIRED", 0)

    lines.append(f"# Daily Hiring Pipeline Status — {TODAY.strftime('%B %d, %Y')}")
    lines.append(f"**Hiring Manager:** Vibhu Talwar  ")
    lines.append(f"**Generated:** {TODAY.isoformat()} (auto-update, 10:00 AM IST)  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Executive Summary ──────────────────────────────────────────────────────
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Positions Filled | {filled} / {needed} |")
    lines.append(f"| Hired | {hired_count} |")
    lines.append(f"| Active Primary Candidates | {primary_count} |")
    lines.append(f"| Backup Candidates | {counts.get('BACKUP', 0)} |")
    lines.append(f"| Rejected / Excluded / Backed Out | "
                 f"{counts.get('REJECTED', 0) + counts.get('EXCLUDED', 0) + counts.get('BACKED_OUT', 0)} |")
    lines.append("")

    # ── Today's Priority Actions ───────────────────────────────────────────────
    priority_candidates = sorted(
        [c for c in CANDIDATES if c.get("priority")],
        key=lambda x: x["priority"],
    )
    lines.append("## Today's Priority Actions")
    lines.append("")
    if priority_candidates:
        for c in priority_candidates:
            pos = POSITIONS[c["position"]]["title"]
            emoji = STATUS_EMOJI.get(c["status"], "")
            lines.append(f"### Priority {c['priority']} — {emoji} {c['name']} ({pos})")
            lines.append(f"- **Status:** {c['status']}")
            lines.append(f"- **Score:** {c.get('score', 'N/A')}/10")
            if c.get("offer"):
                lines.append(f"- **Offer:** {c['offer']}")
            if c.get("contact"):
                lines.append(f"- **Contact:** {c['contact']}")
            if c.get("joining"):
                lines.append(f"- **Joining:** {c['joining'].strftime('%B %d, %Y')} ({days_label(c['joining'])})")
            lines.append(f"- **Action:** {c['action']}")
            lines.append("")
    else:
        lines.append("_No priority actions defined._")
        lines.append("")

    # ── Position Summaries ─────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Position Summaries")
    lines.append("")
    for pos_id, pos in POSITIONS.items():
        remaining = pos["target"] - pos["hired"]
        urgency = "🔴 URGENT" if remaining > 0 else "🟢 FILLED"
        lines.append(f"### {pos['title']} ({pos_id})")
        lines.append(f"**Target:** {pos['target']} | **Hired:** {pos['hired']} | "
                     f"**Still Needed:** {remaining} — {urgency}")
        lines.append("")
        pos_candidates = [c for c in CANDIDATES if c["position"] == pos_id]
        lines.append("| Name | ID | Status | Score | Action |")
        lines.append("|------|----|--------|-------|--------|")
        for c in pos_candidates:
            emoji = STATUS_EMOJI.get(c["status"], "")
            score_str = f"{c['score']}/10" if c.get("score") else "—"
            lines.append(
                f"| {c['name']} | {c['id']} | {emoji} {c['status']} "
                f"| {score_str} | {c['action']} |"
            )
        lines.append("")

    # ── Key Upcoming Dates ─────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Key Upcoming Dates")
    lines.append("")
    joining_candidates = [c for c in CANDIDATES if c.get("joining")]
    joining_candidates.sort(key=lambda x: x["joining"])
    lines.append("| Candidate | Role | Joining Date | Days Away |")
    lines.append("|-----------|------|--------------|-----------|")
    for c in joining_candidates:
        pos_title = POSITIONS[c["position"]]["title"]
        lines.append(
            f"| {c['name']} | {pos_title} | "
            f"{c['joining'].strftime('%B %d, %Y')} | {days_label(c['joining'])} |"
        )
    lines.append("")

    # ── Full Candidate Status Table ────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Full Candidate Status")
    lines.append("")
    lines.append("| # | Name | ID | Position | Status | Score |")
    lines.append("|---|------|----|----------|--------|-------|")
    for i, c in enumerate(CANDIDATES, 1):
        emoji = STATUS_EMOJI.get(c["status"], "")
        score_str = f"{c['score']}/10" if c.get("score") else "—"
        pos_title = POSITIONS[c["position"]]["title"].split("/")[0].strip()
        lines.append(
            f"| {i} | {c['name']} | {c['id']} | {pos_title} "
            f"| {emoji} {c['status']} | {score_str} |"
        )
    lines.append("")
    lines.append("---")
    lines.append(f"_Report auto-generated on {TODAY.isoformat()} at 10:00 AM IST_")
    lines.append("")
    return "\n".join(lines)


def main():
    report = generate_report()
    output_file = "PIPELINE_DAILY_STATUS.md"
    with open(output_file, "w") as f:
        f.write(report)
    print(f"Daily pipeline status written to {output_file}")
    print(report)


if __name__ == "__main__":
    main()
