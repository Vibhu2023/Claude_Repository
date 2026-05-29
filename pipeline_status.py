"""
Generates a daily hiring pipeline status report from candidates.json.
Outputs DAILY_PIPELINE_STATUS.md with today's snapshot.
"""

import json
import os
from datetime import date, datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🎯",
    "BACKUP": "🔄",
    "OPTIONAL": "💡",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}

STATUS_LABEL = {
    "HIRED": "Hired",
    "PRIMARY": "Primary",
    "BACKUP": "Backup",
    "OPTIONAL": "Optional",
    "ON_HOLD": "On Hold",
    "EXCLUDED": "Excluded",
    "REJECTED": "Rejected",
    "WITHDRAWN": "Withdrawn",
    "BACKED_OUT": "Backed Out",
}

URGENCY_EMOJI = {"CRITICAL": "🔴", "URGENT": "🟠", "NORMAL": "🟢"}


def load_data(path="candidates.json"):
    with open(path) as f:
        return json.load(f)


def days_until(date_str):
    if not date_str:
        return None
    try:
        target = date.fromisoformat(date_str)
        delta = (target - date.today()).days
        return delta
    except ValueError:
        return None


def format_days(delta):
    if delta is None:
        return ""
    if delta < 0:
        return f"({abs(delta)}d ago)"
    if delta == 0:
        return "(TODAY)"
    return f"(in {delta}d)"


def build_report(data):
    today = datetime.now(IST)
    today_str = today.strftime("%B %d, %Y")
    time_str = today.strftime("%I:%M %p IST")

    positions = {p["id"]: p for p in data["positions"]}
    candidates = data["candidates"]
    key_dates = data.get("key_dates", [])

    total_target = sum(p["target"] for p in data["positions"])
    total_hired = sum(p["hired"] for p in data["positions"])
    total_remaining = total_target - total_hired

    primaries = [c for c in candidates if c["status"] == "PRIMARY"]
    backups = [c for c in candidates if c["status"] == "BACKUP"]

    lines = []

    lines.append(f"# Hiring Pipeline — Daily Status")
    lines.append(f"**{today_str}** | Generated: {time_str}  ")
    lines.append(f"**Hiring Manager:** {data['hiring_manager']} | {data['organization']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive snapshot
    lines.append("## Executive Snapshot")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Open Positions | {len(data['positions'])} |")
    lines.append(f"| Total Slots Required | {total_target} |")
    lines.append(f"| Hired | {total_hired} |")
    lines.append(f"| **Still Needed** | **{total_remaining}** |")
    lines.append(f"| Active Primary Candidates | {len(primaries)} |")
    lines.append(f"| Backup Candidates | {len(backups)} |")
    lines.append("")

    # Per-position status
    lines.append("## Position Status")
    lines.append("")

    for pos in data["positions"]:
        urgency = URGENCY_EMOJI.get(pos["urgency"], "")
        filled = pos["hired"]
        needed = pos["target"] - filled
        lines.append(f"### {urgency} {pos['title']} ({pos['id']})")
        lines.append(
            f"**Target:** {pos['target']} &nbsp;|&nbsp; "
            f"**Hired:** {filled} &nbsp;|&nbsp; "
            f"**Still Needed:** {needed} &nbsp;|&nbsp; "
            f"**Status:** {pos['urgency']}"
        )
        lines.append("")

        pos_candidates = [c for c in candidates if c["position_id"] == pos["id"]]
        active = [c for c in pos_candidates if c["status"] in ("HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD")]

        if active:
            lines.append("| Candidate | Status | Score | Offer | Notice | Joining | Priority |")
            lines.append("|-----------|--------|-------|-------|--------|---------|----------|")
            for c in sorted(active, key=lambda x: (x["status"] != "HIRED", x.get("priority") or 99, -(x.get("score") or 0))):
                emoji = STATUS_EMOJI.get(c["status"], "")
                label = STATUS_LABEL.get(c["status"], c["status"])
                score = f"{c['score']}/10" if c.get("score") else "—"
                offer = f"₹{c['offer_ctc']}" if c.get("offer_ctc") else "—"
                notice = f"{c['notice_days']}d" if c.get("notice_days") is not None and c["notice_days"] > 0 else ("Immediate" if c.get("notice_days") == 0 else "—")
                jd = c.get("joining_date", "")
                delta = days_until(jd)
                joining = f"{jd} {format_days(delta)}" if jd else "—"
                priority = c.get("priority_label") or ("—" if c["status"] not in ("HIRED",) else "Confirmed")
                lines.append(f"| {c['name']} | {emoji} {label} | {score} | {offer} | {notice} | {joining} | {priority} |")
        lines.append("")

    # Priority actions
    priority_candidates = sorted(
        [c for c in candidates if c.get("priority") is not None],
        key=lambda x: x["priority"]
    )

    if priority_candidates:
        lines.append("---")
        lines.append("")
        lines.append("## Priority Actions Today")
        lines.append("")
        for c in priority_candidates:
            pos = positions.get(c["position_id"], {})
            lines.append(f"### Priority {c['priority']} — {c['name']} ({pos.get('title', c['position'])})")
            lines.append(f"**Action:** {c.get('priority_label', 'Contact')}  ")
            if c.get("email"):
                lines.append(f"**Email:** {c['email']}  ")
            if c.get("phone"):
                lines.append(f"**Phone:** {c['phone']}  ")
            if c.get("offer_ctc"):
                lines.append(f"**Offer:** ₹{c['offer_ctc']}  ")
            if c.get("notice_days") is not None:
                notice_str = "Immediate" if c["notice_days"] == 0 else f"{c['notice_days']} days"
                lines.append(f"**Notice Period:** {notice_str}  ")
            if c.get("notes"):
                lines.append(f"**Notes:** {c['notes']}  ")
            lines.append("")

    # Upcoming key dates
    if key_dates:
        lines.append("---")
        lines.append("")
        lines.append("## Upcoming Key Dates")
        lines.append("")
        lines.append("| Date | Event | Days Away |")
        lines.append("|------|-------|-----------|")
        for kd in sorted(key_dates, key=lambda x: x["date"]):
            delta = days_until(kd["date"])
            countdown = format_days(delta)
            lines.append(f"| {kd['date']} | {kd['event']} | {countdown} |")
        lines.append("")

    # Risk alerts
    lines.append("---")
    lines.append("")
    lines.append("## Risk Alerts")
    lines.append("")

    risks = []
    for pos in data["positions"]:
        pos_primaries = [c for c in candidates if c["position_id"] == pos["id"] and c["status"] == "PRIMARY"]
        pos_backups = [c for c in candidates if c["position_id"] == pos["id"] and c["status"] == "BACKUP"]
        if not pos_primaries and pos["hired"] < pos["target"]:
            risks.append(f"🔴 **{pos['title']}**: No primary candidate — position unfilled with no active pursuit")
        elif len(pos_primaries) == 1 and not pos_backups:
            risks.append(f"🟠 **{pos['title']}**: Single primary candidate ({pos_primaries[0]['name']}) with zero backup — high risk if candidate declines")
        elif pos["urgency"] == "CRITICAL" and pos["hired"] == 0:
            risks.append(f"🔴 **{pos['title']}**: CRITICAL — 0/{pos['target']} hired")

    backed_out = [c for c in candidates if c["status"] == "BACKED_OUT"]
    if backed_out:
        for c in backed_out:
            risks.append(f"⚠️ **{c['name']}** backed out after offer acceptance ({c['position']})")

    if risks:
        for r in risks:
            lines.append(f"- {r}")
    else:
        lines.append("- No critical risks at this time.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Auto-generated daily at 10:00 AM IST. Edit `candidates.json` to update candidate data.*")

    return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "candidates.json")
    output_path = os.path.join(script_dir, "DAILY_PIPELINE_STATUS.md")

    data = load_data(data_path)
    report = build_report(data)

    with open(output_path, "w") as f:
        f.write(report)
    print(f"Pipeline status report written to {output_path}")


if __name__ == "__main__":
    main()
