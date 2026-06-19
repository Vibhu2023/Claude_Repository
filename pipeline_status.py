"""
Daily Hiring Pipeline Status Generator - Moolchand Healthcare Group
Generates a morning status report with overdue flags, today's actions, and upcoming milestones.
Run daily at 10 AM to produce DAILY_STATUS.md.
"""

from datetime import date, datetime, timedelta

TODAY = date.today()

POSITIONS = {
    "FIN-001": {"title": "Sr Finance Manager / Finance & AR Lead", "target": 2, "hired": 1},
    "RPA-001": {"title": "RPA Developer", "target": 2, "hired": 0},
    "DRO-001": {"title": "Chief Digital Revenue Officer", "target": 1, "hired": 0},
}

CANDIDATES = [
    # Finance
    {
        "id": "FIN-JAT-001", "name": "Jatin Sachdeva", "position": "FIN-001",
        "status": "HIRED", "score": 7.2,
        "offer_ctc": "₹4.5L", "joining_date": date(2026, 6, 18),
        "source": "GIST Consulting", "notes": "Confirmed joining June 18, 2026",
    },
    {
        "id": "FIN-RAH-001", "name": "CA Rahul Madaan", "position": "FIN-001",
        "status": "PRIMARY", "score": 8.8,
        "offer_ctc": "₹42-44L", "notice_days": 30, "est_start": date(2026, 6, 15),
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "action": "CONTACT TODAY - ONLY viable option after rejections",
        "action_deadline": date(2026, 5, 19),
    },
    {
        "id": "FIN-ABH-001", "name": "CA Abhishek Goyal", "position": "FIN-001",
        "status": "REJECTED", "score": 9.3, "notes": "Declined offer",
    },
    {
        "id": "FIN-VIK-001", "name": "Vikas Jain", "position": "FIN-001",
        "status": "REJECTED", "score": 7.5, "notes": "Rejected by Moolchand - SAP gap",
    },
    {
        "id": "FIN-MAN-001", "name": "CA Manu Singla", "position": "FIN-001",
        "status": "BACKUP", "score": 8.9, "notes": "Too junior (3 years)",
    },
    {
        "id": "FIN-JAT-002", "name": "CA Jatin Anand", "position": "FIN-001",
        "status": "BACKUP", "score": 8.5, "notes": "6 years experience",
    },
    {
        "id": "FIN-KAP-001", "name": "CA Kapil Sharma", "position": "FIN-001",
        "status": "BACKUP", "score": 7.8, "notes": "7 years experience",
    },
    {
        "id": "FIN-RIT-001", "name": "Ritu Arora", "position": "FIN-001",
        "status": "BACKUP", "score": 8.2, "notes": "7 years, high CTC ₹31.67L",
    },
    {
        "id": "FIN-SHU-001", "name": "Shukla Satia", "position": "FIN-001",
        "status": "BACKUP", "score": 7.8, "notes": "6 years experience",
    },
    # RPA
    {
        "id": "RPA-RIT-001", "name": "Ritik Gupta", "position": "RPA-001",
        "status": "BACKED_OUT", "score": 8.8,
        "notes": "Was confirmed - withdrew after acceptance",
    },
    {
        "id": "RPA-KAM-001", "name": "Kamal", "position": "RPA-001",
        "status": "PRIMARY", "score": 7.8,
        "offer_ctc": "₹6.6L", "notice_days": 90, "est_start": date(2026, 7, 1),
        "contact": "Via GIST - Hemant Kulasri",
        "action": "CONTACT THIS WEEK - Offer ₹6.6L, negotiate notice 90→60 days",
        "action_deadline": date(2026, 5, 21),
    },
    {
        "id": "RPA-ANS-001", "name": "Anshul Vashisth", "position": "RPA-001",
        "status": "PRIMARY", "score": 8.8,
        "offer_ctc": "₹6L + ₹2-3L SAP training", "notice_days": 0, "est_start": date(2026, 7, 1),
        "contact": "From resume",
        "action": "CONTACT WEEK 2 - Offer ₹6L + training budget",
        "action_deadline": date(2026, 5, 28),
    },
    {
        "id": "RPA-SHA-001", "name": "Shahe Faisal", "position": "RPA-001",
        "status": "OPTIONAL", "score": 8.5,
        "offer_ctc": "₹13-15L", "notice_days": 15,
        "notes": "Premium tier - requires budget approval",
    },
    {
        "id": "RPA-SUB-001", "name": "Subrat", "position": "RPA-001",
        "status": "EXCLUDED", "score": 0, "notes": "Limited enterprise experience",
    },
    {
        "id": "RPA-JAS-001", "name": "Jasmin Bar", "position": "RPA-001",
        "status": "EXCLUDED", "score": 0, "notes": "Limited enterprise experience",
    },
    {
        "id": "RPA-HAR-001", "name": "Hardik Agarwal", "position": "RPA-001",
        "status": "EXCLUDED", "score": 0, "notes": "Junior, mentorship-pair only",
    },
    # DRO
    {
        "id": "DRO-KUW-001", "name": "Kuwarjeet Sidana", "position": "DRO-001",
        "status": "PRIMARY", "score": 9.5,
        "offer_ctc": "₹28L", "notice_days": 30, "est_start": date(2026, 6, 30),
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "action": "INTERVIEW THIS WEEK - Offer ₹28L",
        "action_deadline": date(2026, 5, 21),
    },
]

MILESTONES = [
    {"date": date(2026, 6, 18), "label": "Jatin Sachdeva joins (Finance)", "status": "JOINING"},
    {"date": date(2026, 6, 30), "label": "Kuwarjeet Sidana expected start (DRO)", "status": "TARGET"},
    {"date": date(2026, 7, 1),  "label": "Kamal + Anshul expected start (RPA)", "status": "TARGET"},
]

STATUS_EMOJI = {
    "HIRED": "✅", "PRIMARY": "🎯", "BACKUP": "🔄", "OPTIONAL": "💡",
    "REJECTED": "❌", "EXCLUDED": "🚫", "BACKED_OUT": "⚠️", "ON_HOLD": "⏸️",
}

STATUS_LABEL = {
    "HIRED": "Hired", "PRIMARY": "Primary", "BACKUP": "Backup", "OPTIONAL": "Optional",
    "REJECTED": "Rejected", "EXCLUDED": "Excluded", "BACKED_OUT": "Backed Out", "ON_HOLD": "On Hold",
}


def days_label(d: date) -> str:
    delta = (d - TODAY).days
    if delta < 0:
        return f"{abs(delta)}d overdue"
    if delta == 0:
        return "TODAY"
    return f"in {delta}d"


def milestone_flag(d: date) -> str:
    delta = (d - TODAY).days
    if delta < 0:
        return f"✅ {abs(delta)} day(s) ago"
    if delta == 0:
        return "📅 TODAY"
    if delta <= 7:
        return f"⚠️  in {delta}d"
    return f"🔵 in {delta}d"


def build_report() -> str:
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines += [
        f"# Daily Pipeline Status — {TODAY.strftime('%B %d, %Y')}",
        f"**Generated:** {ts}  ",
        f"**Hiring Manager:** Vibhu Talwar  ",
        f"**Organisation:** Moolchand Healthcare Group  ",
        "",
        "---",
        "",
    ]

    # ── Executive snapshot ──────────────────────────────────────────────────
    hired       = [c for c in CANDIDATES if c["status"] == "HIRED"]
    primary     = [c for c in CANDIDATES if c["status"] == "PRIMARY"]
    backup      = [c for c in CANDIDATES if c["status"] == "BACKUP"]
    backed_out  = [c for c in CANDIDATES if c["status"] == "BACKED_OUT"]
    total_open  = sum(p["target"] - p["hired"] for p in POSITIONS.values())

    lines += [
        "## Executive Snapshot",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Open Positions | {total_open} of {sum(p['target'] for p in POSITIONS.values())} |",
        f"| Hired (confirmed) | {len(hired)} |",
        f"| Primary Candidates | {len(primary)} |",
        f"| Backup Candidates  | {len(backup)} |",
        f"| Backed Out (risk)  | {len(backed_out)} |",
        "",
    ]

    # ── Overdue actions ──────────────────────────────────────────────────────
    overdue = [c for c in CANDIDATES if "action_deadline" in c and c["action_deadline"] < TODAY]
    if overdue:
        lines += [
            "## 🚨 Overdue Actions",
            "",
        ]
        for c in overdue:
            days_late = (TODAY - c["action_deadline"]).days
            lines += [
                f"### {c['name']} ({c['id']}) — {days_late}d overdue",
                f"- **Position:** {POSITIONS[c['position']]['title']}",
                f"- **Score:** {c['score']}/10",
                f"- **Action:** {c.get('action', 'N/A')}",
                f"- **Deadline was:** {c['action_deadline'].strftime('%B %d, %Y')}",
                f"- **Contact:** {c.get('contact', 'N/A')}",
                "",
            ]

    # ── Today's priority actions ─────────────────────────────────────────────
    today_actions = [c for c in CANDIDATES if "action_deadline" in c and c["action_deadline"] == TODAY]
    upcoming_7d   = [c for c in CANDIDATES if "action_deadline" in c
                     and TODAY < c["action_deadline"] <= TODAY + timedelta(days=7)]

    if today_actions:
        lines += ["## 📌 Priority Actions — Today", ""]
        for c in today_actions:
            lines += [
                f"- **{c['name']}** ({POSITIONS[c['position']]['title']}) — {c.get('action', '')}",
                f"  Contact: {c.get('contact', 'N/A')}",
                "",
            ]

    if upcoming_7d:
        lines += ["## 📅 Coming Up (Next 7 Days)", ""]
        for c in upcoming_7d:
            lines += [
                f"- **{c['name']}** — {c.get('action', '')} "
                f"({c['action_deadline'].strftime('%b %d')})",
            ]
        lines.append("")

    # ── Milestones ───────────────────────────────────────────────────────────
    lines += ["## 🗓️ Joining Milestones", ""]
    for m in MILESTONES:
        lines.append(f"- {milestone_flag(m['date'])}  **{m['label']}** ({m['date'].strftime('%b %d, %Y')})")
    lines.append("")

    # ── Position-by-position status ──────────────────────────────────────────
    lines += ["## Position Status", ""]

    for pos_id, pos in POSITIONS.items():
        remaining = pos["target"] - pos["hired"]
        urgency = "CRITICAL" if pos["hired"] == 0 else "URGENT" if remaining > 0 else "FILLED"
        lines += [
            f"### {pos['title']} ({pos_id})",
            f"**Target:** {pos['target']} | **Hired:** {pos['hired']} | "
            f"**Remaining:** {remaining} | **Status:** {urgency}",
            "",
            "| Candidate | Score | Status | CTC Offer | Est. Start / Notes |",
            "|-----------|-------|--------|-----------|--------------------|",
        ]
        pos_candidates = [c for c in CANDIDATES if c["position"] == pos_id
                          and c["status"] not in ("EXCLUDED",)]
        for c in pos_candidates:
            emoji = STATUS_EMOJI.get(c["status"], "")
            label = STATUS_LABEL.get(c["status"], c["status"])
            ctc   = c.get("offer_ctc", "—")
            if "est_start" in c:
                extra = f"Start: {c['est_start'].strftime('%b %d')} ({days_label(c['est_start'])})"
            elif "joining_date" in c:
                extra = f"Join: {c['joining_date'].strftime('%b %d')} ({days_label(c['joining_date'])})"
            else:
                extra = c.get("notes", "—")
            lines.append(
                f"| {c['name']} | {c['score']}/10 | {emoji} {label} | {ctc} | {extra} |"
            )
        lines += ["", ""]

    # ── Full candidate roster ────────────────────────────────────────────────
    lines += [
        "## Full Candidate Roster",
        "",
        "| ID | Name | Position | Status | Score |",
        "|----|------|----------|--------|-------|",
    ]
    for c in CANDIDATES:
        emoji = STATUS_EMOJI.get(c["status"], "")
        label = STATUS_LABEL.get(c["status"], c["status"])
        pos_title = POSITIONS[c["position"]]["title"].split("/")[0].strip()
        lines.append(f"| {c['id']} | {c['name']} | {pos_title} | {emoji} {label} | {c['score']}/10 |")
    lines += [
        "",
        "---",
        "",
        f"**Report Generated:** {ts}  ",
        "**Source:** Moolchand Healthcare Group Hiring Pipeline  ",
        "**Next Scheduled Update:** Tomorrow 10:00 AM  ",
    ]

    return "\n".join(lines) + "\n"


def main():
    report = build_report()
    out_path = "DAILY_STATUS.md"
    with open(out_path, "w") as f:
        f.write(report)
    print(f"Daily pipeline status written to {out_path} ({TODAY})")


if __name__ == "__main__":
    main()
