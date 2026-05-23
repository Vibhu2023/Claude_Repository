#!/usr/bin/env python3
"""
Generates a daily hiring pipeline status report from pipeline_data.json.
Run manually or via GitHub Actions cron at 10 AM IST daily.
"""
import json
from datetime import date
from pathlib import Path

TIER_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "⭐",
    "BACKUP": "📋",
    "OPTIONAL": "💡",
    "ON_HOLD": "⏸️",
    "EXCLUDED": "🚫",
    "REJECTED": "❌",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}

ACTIVE_TIERS = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL"}
ACTION_TIERS = {"HIRED", "PRIMARY"}


def days_until(date_str):
    if not date_str:
        return None
    return (date.fromisoformat(date_str) - date.today()).days


def load_data():
    data_file = Path(__file__).parent / "pipeline_data.json"
    with open(data_file) as f:
        return json.load(f)


def build_report(data):
    today = date.today()
    today_label = today.strftime("%B %d, %Y (%A)")
    positions = {p["id"]: p for p in data["positions"]}
    candidates = data["candidates"]

    overdue, due_today, upcoming = [], [], []
    for c in candidates:
        if c["tier"] not in ACTION_TIERS or not c.get("action_deadline"):
            continue
        delta = days_until(c["action_deadline"])
        if delta is None:
            continue
        if delta < 0:
            overdue.append((c, abs(delta)))
        elif delta == 0:
            due_today.append(c)
        elif delta <= 7:
            upcoming.append((c, delta))

    overdue.sort(key=lambda x: -x[1])
    upcoming.sort(key=lambda x: x[1])

    lines = [
        f"# Daily Hiring Pipeline Status",
        f"**Date:** {today_label}",
        f"**Organization:** {data['meta']['organization']}",
        f"**Hiring Manager:** {data['meta']['hiring_manager']}",
        "",
        "---",
        "",
    ]

    # Overall health banner
    total_target = sum(p["target_count"] for p in data["positions"])
    total_hired = sum(p["hired_count"] for p in data["positions"])
    remaining = total_target - total_hired
    lines += [
        f"## Pipeline Health: {total_hired}/{total_target} positions filled | {remaining} remaining",
        "",
    ]

    # Overdue actions
    if overdue:
        lines.append("## 🚨 OVERDUE ACTIONS")
        for c, days_late in overdue:
            pos = positions.get(c.get("position_id"), {})
            pos_title = pos.get("title", c.get("position_id", "—"))
            contact = " | ".join(filter(None, [c.get("phone"), c.get("email")]))
            lines += [
                f"- **{c['name']}** — {pos_title} ({days_late}d overdue)",
                f"  - Action: {c.get('action_required', '—')}",
            ]
            if contact:
                lines.append(f"  - Contact: {contact}")
        lines.append("")

    # Today's actions
    if due_today:
        lines.append("## ✅ TODAY'S PRIORITIES")
        for c in due_today:
            pos = positions.get(c.get("position_id"), {})
            pos_title = pos.get("title", c.get("position_id", "—"))
            contact = " | ".join(filter(None, [c.get("phone"), c.get("email")]))
            lines += [
                f"- **{c['name']}** — {pos_title}",
                f"  - Action: {c.get('action_required', '—')}",
            ]
            if contact:
                lines.append(f"  - Contact: {contact}")
        lines.append("")

    if not overdue and not due_today:
        lines += ["## ✅ No actions due today", ""]

    # Upcoming this week
    if upcoming:
        lines.append("## 📅 UPCOMING THIS WEEK")
        for c, days in upcoming:
            pos = positions.get(c.get("position_id"), {})
            pos_title = pos.get("title", c.get("position_id", "—"))
            lines.append(
                f"- **{c['name']}** — {pos_title} (due in {days}d on {c['action_deadline']})"
            )
            lines.append(f"  - Action: {c.get('action_required', '—')}")
        lines.append("")

    # Position summary table
    lines += [
        "## 📊 Position Summary",
        "",
        "| Position | Target | Hired | Still Needed | Urgency |",
        "|----------|-------:|------:|-------------:|---------|",
    ]
    for pos in data["positions"]:
        need = pos["target_count"] - pos["hired_count"]
        lines.append(
            f"| {pos['title']} | {pos['target_count']} | {pos['hired_count']} | {need} | **{pos['urgency']}** |"
        )
    lines.append("")

    # Active candidate board by position
    lines.append("## 📋 Candidate Status Board")
    lines.append("")
    for pos in data["positions"]:
        pos_candidates = [
            c for c in candidates
            if c.get("position_id") == pos["id"] and c["tier"] in ACTIVE_TIERS
        ]
        if not pos_candidates:
            continue
        lines.append(f"### {pos['title']} ({pos['id']})")
        for c in pos_candidates:
            emoji = TIER_EMOJI.get(c["tier"], "❓")
            score = f"{c['score']}/10" if c.get("score") else "N/A"
            ctc = c.get("offer_ctc") or c.get("current_ctc") or "—"
            lines.append(
                f"- {emoji} **{c['name']}** `[{c['tier']}]` Score: {score} | CTC: ₹{ctc}"
            )
            lines.append(f"  - {c.get('status_detail', '—')}")
        lines.append("")

    # Joining countdown
    joining = [
        c for c in candidates if c.get("joining_date") and days_until(c["joining_date"]) is not None and days_until(c["joining_date"]) >= 0
    ]
    if joining:
        lines.append("## 📆 Joining Countdown")
        for c in sorted(joining, key=lambda x: x["joining_date"]):
            d = days_until(c["joining_date"])
            lines.append(f"- **{c['name']}** → {c['joining_date']} ({d} day{'s' if d != 1 else ''} away)")
        lines.append("")

    lines += [
        "---",
        f"*Auto-generated at 10:00 AM IST | Data last manually updated: {data['meta']['last_updated']}*",
        f"*To update candidate status, edit `pipeline_data.json` and push to trigger a fresh report.*",
    ]

    return "\n".join(lines) + "\n"


def main():
    data = load_data()
    report = build_report(data)
    out = Path(__file__).parent / "DAILY_PIPELINE_STATUS.md"
    out.write_text(report)
    print(f"Report written to {out}")
    print()
    print(report)


if __name__ == "__main__":
    main()
