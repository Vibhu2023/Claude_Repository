#!/usr/bin/env python3
"""
Daily hiring pipeline status update generator for Moolchand Healthcare Group.

Usage:
    python3 daily_pipeline_update.py           # Print report to stdout
    python3 daily_pipeline_update.py --save    # Also save as dated .md file

Cron setup (runs daily at 10:00 AM):
    0 10 * * * /usr/bin/python3 /path/to/daily_pipeline_update.py --save >> /path/to/logs/pipeline.log 2>&1
"""

import json
import sys
import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "candidates_data.json"
REPORTS_DIR = Path(__file__).parent / "daily_reports"

STATUS_LABELS = {
    "hired":      ("HIRED",       "✅"),
    "offer_sent": ("OFFER SENT",  "📩"),
    "offered":    ("OFFERED",     "💼"),
    "interviewed":("INTERVIEWED", "🗣️"),
    "primary":    ("PRIMARY",     "🔴"),
    "backup":     ("BACKUP",      "🟡"),
    "optional":   ("OPTIONAL",    "🔵"),
    "on_hold":    ("ON HOLD",     "⏸️"),
    "backed_out": ("BACKED OUT",  "↩️"),
    "withdrawn":  ("WITHDRAWN",   "🚫"),
    "rejected":   ("REJECTED",    "❌"),
    "excluded":   ("EXCLUDED",    "⛔"),
}

ACTIVE_STATUSES = {"hired", "offer_sent", "offered", "interviewed", "primary", "backup", "optional", "on_hold"}


def load_data():
    if not DATA_FILE.exists():
        print(f"ERROR: Data file not found: {DATA_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(DATA_FILE) as f:
        return json.load(f)


def days_until(date_str):
    if not date_str:
        return None
    try:
        target = datetime.date.fromisoformat(date_str)
        delta = (target - datetime.date.today()).days
        return delta
    except ValueError:
        return None


def format_ctc(ctc):
    return f"₹{ctc}" if ctc else "—"


def generate_report(data):
    today = datetime.date.today()
    candidates = data["candidates"]
    positions = data["positions"]
    actions = data.get("actions", [])

    lines = []

    # Header
    lines += [
        f"# {data['organization']} — Daily Hiring Pipeline Update",
        f"**Date:** {today.strftime('%A, %B %d, %Y')}  ",
        f"**Hiring Manager:** {data['hiring_manager']}  ",
        f"**Data Last Updated:** {data.get('last_updated', 'Unknown')}",
        "",
        "---",
        "",
    ]

    # Executive Summary
    status_counts = {}
    for c in candidates:
        s = c["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    total_target = sum(p["target"] for p in positions)
    total_hired = status_counts.get("hired", 0)
    positions_filled = sum(
        1 for p in positions
        if sum(1 for c in candidates if c["position_id"] == p["id"] and c["status"] == "hired") >= p["target"]
    )

    lines += [
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **Open Positions** | {len(positions)} |",
        f"| **Total Slots** | {total_target} |",
        f"| **Positions Fully Filled** | {positions_filled} / {len(positions)} |",
        f"| **Total Hired** | {total_hired} / {total_target} |",
        f"| **Total Candidates Tracked** | {len(candidates)} |",
        "",
    ]

    for status in ["hired", "offer_sent", "offered", "interviewed", "primary", "backup", "optional", "on_hold", "backed_out", "withdrawn", "rejected", "excluded"]:
        count = status_counts.get(status, 0)
        if count > 0:
            label, emoji = STATUS_LABELS[status]
            lines.append(f"| {emoji} **{label}** | {count} |")

    lines += ["", "---", ""]

    # Today's priority actions
    pending_actions = [a for a in actions if not a.get("completed")]
    overdue_actions = []
    due_today = []
    upcoming_actions = []

    for a in pending_actions:
        d = days_until(a.get("due_date"))
        if d is None:
            upcoming_actions.append((a, None))
        elif d < 0:
            overdue_actions.append((a, d))
        elif d == 0:
            due_today.append((a, d))
        else:
            upcoming_actions.append((a, d))

    lines += ["## Today's Action Items", ""]

    if overdue_actions:
        lines.append("### 🚨 OVERDUE")
        for a, d in overdue_actions:
            lines.append(f"- **{a['priority']}** *(overdue by {abs(d)} day{'s' if abs(d) != 1 else ''})*")
            lines.append(f"  {a['description']}")
            if a.get("contact"):
                lines.append(f"  📞 {a['contact']}")
        lines.append("")

    if due_today:
        lines.append("### ⚡ DUE TODAY")
        for a, _ in due_today:
            lines.append(f"- **{a['priority']}**")
            lines.append(f"  {a['description']}")
            if a.get("contact"):
                lines.append(f"  📞 {a['contact']}")
        lines.append("")

    if upcoming_actions:
        lines.append("### 📅 Upcoming")
        for a, d in upcoming_actions:
            due_str = f"in {d} day{'s' if d != 1 else ''}" if d is not None else "no due date"
            lines.append(f"- **{a['priority']}** *({due_str})*")
            lines.append(f"  {a['description']}")
            if a.get("contact"):
                lines.append(f"  📞 {a['contact']}")
        lines.append("")

    if not pending_actions:
        lines += ["_No pending actions._", ""]

    lines += ["---", ""]

    # Position-by-position breakdown
    lines += ["## Pipeline by Position", ""]

    for pos in positions:
        pos_candidates = [c for c in candidates if c["position_id"] == pos["id"]]
        hired_count = sum(1 for c in pos_candidates if c["status"] == "hired")
        need = pos["target"] - hired_count
        urgency = pos.get("urgency", "")

        fill_bar = "█" * hired_count + "░" * need
        lines += [
            f"### {pos['title']} ({pos['id']}) — {urgency}",
            f"**Progress:** [{fill_bar}] {hired_count}/{pos['target']} filled | Still need: {need}",
            "",
        ]

        for status in ["hired", "offer_sent", "offered", "interviewed", "primary", "backup", "optional", "on_hold", "backed_out", "withdrawn", "rejected", "excluded"]:
            group = [c for c in pos_candidates if c["status"] == status]
            if not group:
                continue

            label, emoji = STATUS_LABELS[status]
            lines.append(f"**{emoji} {label}**")

            for c in group:
                score_str = f" | Score: {c['score']}/10" if c.get("score") else ""
                offer_str = f" | Offer: {format_ctc(c.get('offer_ctc'))}" if c.get("offer_ctc") else ""
                joining = c.get("joining_date")
                if joining:
                    d = days_until(joining)
                    join_str = f" | Joining: {joining}"
                    if d is not None:
                        join_str += f" ({d} days)" if d > 0 else " (TODAY!)" if d == 0 else f" ({abs(d)} days ago)"
                else:
                    join_str = ""
                notice = f" | Notice: {c['notice_period_days']}d" if c.get("notice_period_days") is not None else ""
                lines.append(f"- **{c['name']}** ({c['id']}){score_str}{offer_str}{join_str}{notice}")
                if c.get("notes"):
                    lines.append(f"  _{c['notes']}_")
                if c.get("contact_email") or c.get("contact_phone"):
                    contact_parts = []
                    if c.get("contact_email"):
                        contact_parts.append(c["contact_email"])
                    if c.get("contact_phone"):
                        contact_parts.append(c["contact_phone"])
                    lines.append(f"  📞 {' | '.join(contact_parts)}")

            lines.append("")

        lines += ["---", ""]

    # Upcoming joining dates
    joiners = [
        (c, c["joining_date"])
        for c in candidates
        if c.get("joining_date") and c["status"] in {"hired", "offer_sent", "offered"}
    ]
    joiners.sort(key=lambda x: x[1])

    if joiners:
        lines += ["## Upcoming Joiners", ""]
        lines += [
            "| Candidate | Position | Joining Date | Days Away | Status |",
            "|-----------|----------|--------------|-----------|--------|",
        ]
        for c, jd in joiners:
            pos_title = next((p["title"] for p in positions if p["id"] == c["position_id"]), c["position_id"])
            d = days_until(jd)
            days_str = f"{d} days" if d and d > 0 else "Today!" if d == 0 else f"{abs(d)} days ago"
            _, emoji = STATUS_LABELS.get(c["status"], ("", ""))
            lines.append(f"| {c['name']} | {pos_title} | {jd} | {days_str} | {emoji} |")
        lines += [""]

    # Footer
    lines += [
        "---",
        f"_Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Source: candidates_data.json_",
    ]

    return "\n".join(lines)


def main():
    save_report = "--save" in sys.argv

    data = load_data()
    report = generate_report(data)
    print(report)

    if save_report:
        REPORTS_DIR.mkdir(exist_ok=True)
        today = datetime.date.today()
        report_path = REPORTS_DIR / f"pipeline_{today.isoformat()}.md"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\n[Saved: {report_path}]", file=sys.stderr)


if __name__ == "__main__":
    main()
