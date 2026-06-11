#!/usr/bin/env python3
"""Generate a daily hiring pipeline status report from candidates.json."""

import json
import sys
from datetime import date, datetime
from pathlib import Path

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🎯",
    "BACKUP": "🔄",
    "OPTIONAL": "💡",
    "REJECTED": "❌",
    "BACKED_OUT": "🚫",
    "DO_NOT_SEND": "⛔",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚷",
    "WITHDRAWN": "↩️",
}

URGENCY_EMOJI = {"CRITICAL": "🔴", "URGENT": "🟠", "NORMAL": "🟢"}


def load_data(path: str = "candidates.json") -> dict:
    with open(path) as f:
        return json.load(f)


def days_until(date_str: str | None) -> int | None:
    if not date_str:
        return None
    target = date.fromisoformat(date_str)
    return (target - date.today()).days


def format_ctc(amount: int | None) -> str:
    if amount is None:
        return "N/A"
    lakh = amount / 100_000
    return f"₹{lakh:.1f}L"


def build_report(data: dict) -> str:
    today = date.today()
    now = datetime.now()
    lines: list[str] = []

    meta = data["metadata"]
    positions = {p["id"]: p for p in data["positions"]}
    candidates = data["candidates"]

    # Header
    lines += [
        f"# Daily Hiring Pipeline Status — {today.strftime('%B %d, %Y')}",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M IST')}  ",
        f"**Organisation:** {meta['org']}  ",
        f"**Hiring Manager:** {meta['hiring_manager']}",
        "",
        "---",
        "",
    ]

    # Executive Summary
    status_counts: dict[str, int] = {}
    for c in candidates:
        status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1

    total_needed = sum(p["needed"] for p in data["positions"])
    total_hired = sum(p["hired"] for p in data["positions"])

    lines += [
        "## Executive Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Open Positions | {len(data['positions'])} |",
        f"| Total Hires Needed | {total_needed} |",
        f"| Confirmed Hires | {total_hired} |",
        f"| Active Primary Candidates | {status_counts.get('PRIMARY', 0)} |",
        f"| Backup Candidates | {status_counts.get('BACKUP', 0)} |",
        f"| Rejected / Excluded | {status_counts.get('REJECTED', 0) + status_counts.get('EXCLUDED', 0)} |",
        "",
    ]

    # Overdue actions
    overdue = [
        c for c in candidates
        if c.get("action_deadline") and days_until(c["action_deadline"]) is not None
        and days_until(c["action_deadline"]) < 0
        and c["status"] in ("PRIMARY", "BACKUP")
    ]
    if overdue:
        lines += [
            "## ⚠️ Overdue Actions",
            "",
        ]
        for c in overdue:
            delta = days_until(c["action_deadline"])
            lines.append(
                f"- **{c['name']}** ({c['id']}) — {c['action_required']} "
                f"_(was due {abs(delta)} day{'s' if abs(delta) != 1 else ''} ago)_"
            )
        lines.append("")

    # Today's actions
    due_today = [
        c for c in candidates
        if c.get("action_deadline") and days_until(c["action_deadline"]) is not None
        and 0 <= days_until(c["action_deadline"]) <= 2
        and c["status"] in ("PRIMARY", "BACKUP", "OPTIONAL")
    ]
    if due_today:
        lines += [
            "## 🔔 Actions Due in the Next 48 Hours",
            "",
        ]
        for c in sorted(due_today, key=lambda x: x.get("priority") or 99):
            delta = days_until(c["action_deadline"])
            when = "TODAY" if delta == 0 else f"in {delta} day{'s' if delta != 1 else ''}"
            phone = f" | 📞 {c['contact_phone']}" if c.get("contact_phone") else ""
            email = f" | ✉️ {c['contact_email']}" if c.get("contact_email") else ""
            lines.append(
                f"- **[P{c['priority']}] {c['name']}** ({c['position_id']}) — "
                f"{c['action_required']} _{when}_{phone}{email}"
            )
        lines.append("")

    # Position-by-position breakdown
    lines += ["## Position Status", ""]
    for pos in data["positions"]:
        urgency_icon = URGENCY_EMOJI.get(pos["urgency"], "")
        lines += [
            f"### {urgency_icon} {pos['title']} ({pos['id']})",
            f"**Target:** {pos['target']} | **Hired:** {pos['hired']} | "
            f"**Still Needed:** {pos['needed']} | **Urgency:** {pos['urgency']}",
            "",
            "| Candidate | Score | Status | CTC | Action Deadline | Notes |",
            "|-----------|-------|--------|-----|-----------------|-------|",
        ]

        pos_candidates = [c for c in candidates if c["position_id"] == pos["id"]]
        # Sort: hired first, then by priority, then alphabetically
        pos_candidates.sort(
            key=lambda c: (
                0 if c["status"] == "HIRED" else
                1 if c["status"] == "PRIMARY" else
                2 if c["status"] == "BACKUP" else
                3 if c["status"] == "OPTIONAL" else 4,
                c.get("priority") or 99,
                c["name"],
            )
        )

        for c in pos_candidates:
            icon = STATUS_EMOJI.get(c["status"], "")
            score = f"{c['score']}/10" if c["score"] else "—"
            ctc_display = format_ctc(c["offer_ctc"]) if c["status"] == "HIRED" else format_ctc(c["current_ctc"])
            deadline = c.get("action_deadline") or "—"
            if deadline != "—":
                d = days_until(deadline)
                if d is not None:
                    if d < 0:
                        deadline = f"~~{deadline}~~ _(overdue {abs(d)}d)_"
                    elif d == 0:
                        deadline = f"**{deadline} (TODAY)**"
                    elif d <= 3:
                        deadline = f"**{deadline}** _(in {d}d)_"
            short_note = (c["notes"] or "")[:60] + ("…" if len(c["notes"] or "") > 60 else "")
            lines.append(
                f"| {icon} {c['name']} | {score} | {c['status']} | {ctc_display} | {deadline} | {short_note} |"
            )
        lines.append("")

    # Upcoming joining dates
    joiners = [
        c for c in candidates
        if c.get("joining_date") and c["status"] == "HIRED"
    ]
    if joiners:
        lines += ["## Upcoming Joiners", ""]
        for c in sorted(joiners, key=lambda x: x["joining_date"]):
            d = days_until(c["joining_date"])
            urgency = f"**in {d} days**" if d is not None and d >= 0 else f"_(joined {abs(d)} days ago)_"
            lines.append(
                f"- **{c['name']}** ({c['position_id']}) — Joining {c['joining_date']} {urgency}"
            )
        lines.append("")

    lines += [
        "---",
        "",
        f"_Report auto-generated on {today}. Update `candidates.json` to reflect latest status changes._",
    ]

    return "\n".join(lines)


def main() -> None:
    data_path = Path(__file__).parent / "candidates.json"
    if not data_path.exists():
        print("Error: candidates.json not found.", file=sys.stderr)
        sys.exit(1)

    data = load_data(str(data_path))
    report = build_report(data)

    output_path = Path(__file__).parent / "DAILY_STATUS.md"
    output_path.write_text(report)
    print(f"Daily status report written to {output_path}")
    print(report)


if __name__ == "__main__":
    main()
