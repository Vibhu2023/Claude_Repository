"""
Daily candidate pipeline status generator for Moolchand Healthcare Group.
Run this script daily at 10 AM to produce DAILY_STATUS_UPDATE.md.
"""

from datetime import date, timedelta

TODAY = date.today()

CANDIDATES = {
    "FIN-001": {
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": 1,
        "members": [
            {
                "id": "FIN-JAT-001",
                "name": "Jatin Sachdeva",
                "status": "HIRED",
                "score": 7.2,
                "offer": "₹4.5L",
                "joining": date(2026, 6, 18),
                "notes": "Confirmed. Onboarding prep required.",
            },
            {
                "id": "FIN-RAH-001",
                "name": "CA Rahul Madaan",
                "status": "PRIMARY",
                "score": 8.8,
                "offer": "₹42-44L",
                "joining": None,
                "notes": "30-day notice. Only viable finance option. Contact immediately.",
                "contact": "rahulmadaan942@gmail.com | 9873060422",
            },
            {
                "id": "FIN-MAN-001",
                "name": "CA Manu Singla",
                "status": "BACKUP",
                "score": 8.9,
                "offer": None,
                "joining": None,
                "notes": "Too junior (3 years). Backup only.",
            },
            {
                "id": "FIN-JAT-002",
                "name": "CA Jatin Anand",
                "status": "BACKUP",
                "score": 8.5,
                "offer": None,
                "joining": None,
                "notes": "6 years experience.",
            },
            {
                "id": "FIN-KAP-001",
                "name": "CA Kapil Sharma",
                "status": "BACKUP",
                "score": 7.8,
                "offer": None,
                "joining": None,
                "notes": "7 years experience.",
            },
            {
                "id": "FIN-RIT-001",
                "name": "Ritu Arora",
                "status": "BACKUP",
                "score": 8.2,
                "offer": None,
                "joining": None,
                "notes": "7 years. High CTC ₹31.67L.",
            },
            {
                "id": "FIN-SHU-001",
                "name": "Shukla Satia",
                "status": "BACKUP",
                "score": 7.8,
                "offer": None,
                "joining": None,
                "notes": "6 years experience.",
            },
            {
                "id": "FIN-ABH-001",
                "name": "CA Abhishek Goyal",
                "status": "REJECTED",
                "score": 9.3,
                "offer": None,
                "joining": None,
                "notes": "Declined offer despite highest score.",
            },
            {
                "id": "FIN-VIK-001",
                "name": "Vikas Jain",
                "status": "REJECTED",
                "score": 7.5,
                "offer": None,
                "joining": None,
                "notes": "SAP inexperience. Rejected by Moolchand.",
            },
        ],
    },
    "RPA-001": {
        "title": "RPA Developer",
        "target": 2,
        "hired": 0,
        "members": [
            {
                "id": "RPA-RIT-001",
                "name": "Ritik Gupta",
                "status": "BACKED_OUT",
                "score": 8.8,
                "offer": None,
                "joining": None,
                "notes": "Was hired. Withdrew after acceptance. Team at 0 developers.",
            },
            {
                "id": "RPA-KAM-001",
                "name": "Kamal",
                "status": "PRIMARY",
                "score": 7.8,
                "offer": "₹6.6L",
                "joining": date(2026, 7, 1),
                "notes": "90-day notice (negotiate to 60). Via GIST - Hemant Kulasri.",
                "contact": "Via GIST - Hemant Kulasri",
            },
            {
                "id": "RPA-ANS-001",
                "name": "Anshul Vashisth",
                "status": "PRIMARY",
                "score": 8.8,
                "offer": "₹6L + ₹2-3L training",
                "joining": date(2026, 7, 1),
                "notes": "Immediate notice. SAP FICO integration expertise critical.",
                "contact": "From resume",
            },
            {
                "id": "RPA-SHA-001",
                "name": "Shahe Faisal",
                "status": "OPTIONAL",
                "score": 8.5,
                "offer": "₹13-15L",
                "joining": None,
                "notes": "Capgemini. Competing offers: Cognizant ₹13L, TCS ₹13L. Premium if budget approved.",
            },
            {
                "id": "RPA-SUB-001",
                "name": "Subrat",
                "status": "EXCLUDED",
                "score": None,
                "offer": None,
                "joining": None,
                "notes": "Limited enterprise experience.",
            },
        ],
    },
    "DRO-001": {
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": 0,
        "members": [
            {
                "id": "DRO-KUW-001",
                "name": "Kuwarjeet Sidana",
                "status": "PRIMARY",
                "score": 9.5,
                "offer": "₹28L",
                "joining": date(2026, 6, 30),
                "notes": "10 yrs exp. 30-day notice. NO BACKUP. Must close urgently.",
                "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
            },
        ],
    },
}

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🔵",
    "BACKUP": "🟡",
    "OPTIONAL": "🟣",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}


def days_until(target_date):
    delta = (target_date - TODAY).days
    if delta < 0:
        return f"{abs(delta)} days ago"
    elif delta == 0:
        return "TODAY"
    elif delta == 1:
        return "TOMORROW"
    else:
        return f"in {delta} days"


def urgency_flag(candidate):
    if candidate["status"] == "HIRED" and candidate.get("joining"):
        delta = (candidate["joining"] - TODAY).days
        if 0 <= delta <= 7:
            return " 🚨 JOINING SOON"
    if candidate["status"] == "PRIMARY":
        return " ⚡ ACTION NEEDED"
    return ""


def generate_report():
    lines = []
    lines.append(f"# Daily Pipeline Status — {TODAY.strftime('%B %d, %Y')} (10:00 AM)")
    lines.append(f"**Hiring Manager:** Vibhu Talwar  ")
    lines.append(f"**Organization:** Moolchand Healthcare Group\n")
    lines.append("---\n")

    # --- Executive Summary ---
    total_hired = sum(
        1
        for pos in CANDIDATES.values()
        for c in pos["members"]
        if c["status"] == "HIRED"
    )
    total_primary = sum(
        1
        for pos in CANDIDATES.values()
        for c in pos["members"]
        if c["status"] == "PRIMARY"
    )
    total_backup = sum(
        1
        for pos in CANDIDATES.values()
        for c in pos["members"]
        if c["status"] == "BACKUP"
    )
    total_positions_needed = sum(pos["target"] for pos in CANDIDATES.values())
    positions_filled = sum(pos["hired"] for pos in CANDIDATES.values())

    lines.append("## Executive Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Open Positions | {len(CANDIDATES)} roles ({total_positions_needed} seats) |")
    lines.append(f"| Positions Filled | {positions_filled} / {total_positions_needed} |")
    lines.append(f"| Hired | {total_hired} |")
    lines.append(f"| Active Primaries | {total_primary} |")
    lines.append(f"| Backup Pool | {total_backup} |")
    lines.append(f"| Report Date | {TODAY.strftime('%B %d, %Y')} |\n")

    # --- Upcoming Milestones ---
    lines.append("## ⏰ Upcoming Milestones\n")
    milestones = []
    for pos in CANDIDATES.values():
        for c in pos["members"]:
            if c.get("joining") and c["status"] in ("HIRED", "PRIMARY"):
                delta = (c["joining"] - TODAY).days
                if -7 <= delta <= 30:
                    milestones.append((delta, c["name"], c["status"], c["joining"], pos["title"]))
    milestones.sort()
    if milestones:
        for delta, name, status, joining, role in milestones:
            emoji = "🚨" if delta <= 5 else "📅"
            lines.append(f"- {emoji} **{name}** ({role}) — {joining.strftime('%b %d')} ({days_until(joining)}) [{status}]")
    else:
        lines.append("- No immediate joining milestones in the next 30 days.")
    lines.append("")

    # --- Position-by-position breakdown ---
    lines.append("---\n")
    lines.append("## Position Breakdown\n")

    for pos_id, pos in CANDIDATES.items():
        filled = pos["hired"]
        needed = pos["target"] - filled
        urgency = "🔴 CRITICAL" if filled == 0 else ("🟠 URGENT" if needed > 0 else "🟢 FILLED")
        lines.append(f"### {pos['title']} ({pos_id})")
        lines.append(f"**Target:** {pos['target']} | **Hired:** {filled} | **Still Needed:** {needed} | **Status:** {urgency}\n")

        lines.append("| Candidate | Status | Score | Offer | Joining | Notes |")
        lines.append("|-----------|--------|-------|-------|---------|-------|")
        for c in pos["members"]:
            emoji = STATUS_EMOJI.get(c["status"], "")
            score = f"{c['score']}/10" if c["score"] else "—"
            offer = c["offer"] or "—"
            joining = c["joining"].strftime("%b %d") if c.get("joining") else "—"
            urgency_note = urgency_flag(c)
            notes = c["notes"]
            lines.append(
                f"| **{c['name']}** | {emoji} {c['status']}{urgency_note} | {score} | {offer} | {joining} | {notes} |"
            )
        lines.append("")

    # --- Today's Action Items ---
    lines.append("---\n")
    lines.append("## Today's Action Items\n")

    action_items = []

    for pos in CANDIDATES.values():
        for c in pos["members"]:
            if c["status"] == "HIRED" and c.get("joining"):
                delta = (c["joining"] - TODAY).days
                if 0 <= delta <= 7:
                    action_items.append(
                        f"🚨 **{c['name']}** joining {days_until(c['joining'])} ({c['joining'].strftime('%b %d')}) — confirm onboarding logistics"
                    )
            if c["status"] == "PRIMARY":
                contact = c.get("contact", "")
                contact_str = f" Contact: {contact}" if contact else ""
                action_items.append(
                    f"⚡ **{c['name']}** (PRIMARY) — follow up / confirm offer.{contact_str}"
                )

    if action_items:
        for item in action_items:
            lines.append(f"- {item}")
    else:
        lines.append("- No urgent actions identified for today.")

    lines.append("")
    lines.append("---\n")
    lines.append(f"**Generated automatically on {TODAY.strftime('%B %d, %Y')} at 10:00 AM**  ")
    lines.append("**Next update:** Tomorrow at 10:00 AM")

    return "\n".join(lines)


if __name__ == "__main__":
    report = generate_report()
    output_path = "DAILY_STATUS_UPDATE.md"
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Daily status report written to {output_path}")
    print(report)
