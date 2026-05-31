#!/usr/bin/env python3
"""Generate a daily pipeline status report from candidates.json."""

import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "candidates.json"
OUTPUT_FILE = ROOT / "DAILY_PIPELINE_STATUS.md"

STATUS_EMOJI = {
    "Hired": "✅",
    "Primary": "🎯",
    "Backup": "🔵",
    "Optional": "🟡",
    "On Hold": "⏸️",
    "Excluded": "🚫",
    "Rejected": "❌",
    "Withdrawn": "↩️",
    "Backed Out": "⚠️",
}

URGENCY_EMOJI = {"CRITICAL": "🔴", "URGENT": "🟠", "NORMAL": "🟢"}


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def group_by_position(candidates: list, positions: list) -> dict:
    pos_map = {p["id"]: p for p in positions}
    grouped: dict[str, list] = {p["id"]: [] for p in positions}
    for c in candidates:
        pid = c["position_id"]
        if pid in grouped:
            grouped[pid].append(c)
    return grouped, pos_map


def days_until(date_str: str) -> int:
    target = date.fromisoformat(date_str)
    return (target - date.today()).days


def render_candidate_row(c: dict) -> str:
    emoji = STATUS_EMOJI.get(c["status"], "•")
    score = f"{c['score']}/10" if c["score"] else "N/A"
    ctc = c["offer_ctc"] or "—"
    joining = ""
    if c.get("joining_date"):
        delta = days_until(c["joining_date"])
        joining = f" | Joining: {c['joining_date']} ({delta}d)"
    action = f" | _{c['action']}_" if c.get("action") else ""
    contact = ""
    if c.get("email") or c.get("phone"):
        parts = []
        if c.get("phone"):
            parts.append(c["phone"])
        if c.get("email"):
            parts.append(c["email"])
        contact = f" | 📞 {' / '.join(parts)}"
    return (
        f"| {emoji} **{c['name']}** | {c['status']} | {score} | {ctc}"
        f"{joining}{action}{contact} |"
    )


def count_statuses(candidates: list) -> dict:
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return counts


def build_priority_actions(candidates: list) -> list[dict]:
    primaries = [
        c for c in candidates if c["status"] == "Primary" and c.get("priority")
    ]
    return sorted(primaries, key=lambda x: x["priority"])


def generate_report(data: dict) -> str:
    today = date.today()
    now = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    meta = data["meta"]
    positions = data["positions"]
    candidates = data["candidates"]

    grouped, pos_map = group_by_position(candidates, positions)
    counts = count_statuses(candidates)
    priority_actions = build_priority_actions(candidates)

    total_needed = sum(p["needed"] for p in positions)
    total_hired = sum(p["hired"] for p in positions)

    lines = [
        f"# {meta['organization']} — Daily Pipeline Status",
        f"**Date:** {today}  ",
        f"**Generated:** {now}  ",
        f"**Hiring Manager:** {meta['hiring_manager']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Open Positions | {len(positions)} |",
        f"| Total Candidates Tracked | {len(candidates)} |",
        f"| Hired | {counts.get('Hired', 0)} |",
        f"| Primary (Active) | {counts.get('Primary', 0)} |",
        f"| Backup | {counts.get('Backup', 0)} |",
        f"| Still Needed | {total_needed} |",
        f"| Rejected / Excluded / Backed Out | "
        f"{counts.get('Rejected', 0) + counts.get('Excluded', 0) + counts.get('Backed Out', 0)} |",
        "",
    ]

    # Priority actions today
    if priority_actions:
        lines += [
            "## Today's Priority Actions",
            "",
        ]
        for c in priority_actions:
            pos = pos_map[c["position_id"]]
            contact_str = ""
            if c.get("phone") or c.get("email"):
                parts = []
                if c.get("phone"):
                    parts.append(f"📞 {c['phone']}")
                if c.get("email"):
                    parts.append(f"✉️ {c['email']}")
                contact_str = "  \n  " + " | ".join(parts)
            lines += [
                f"### Priority {c['priority']}: {c['name']} — {pos['title']}",
                f"- **Status:** {STATUS_EMOJI.get(c['status'], '')} {c['status']}",
                f"- **Score:** {c['score']}/10",
                f"- **Offer CTC:** {c['offer_ctc'] or '—'}",
                f"- **Action:** {c['action']}{contact_str}",
                "",
            ]

    # Per-position breakdown
    lines += ["---", "", "## Position Breakdown", ""]

    for pos in positions:
        urgency_icon = URGENCY_EMOJI.get(pos["urgency"], "")
        hired_str = f"{pos['hired']}/{pos['target']} filled"
        lines += [
            f"### {urgency_icon} {pos['title']} ({pos['id']})",
            f"**Target:** {pos['target']} | **Hired:** {pos['hired']} | "
            f"**Still Needed:** {pos['needed']} | **Urgency:** {pos['urgency']}",
            "",
            "| Candidate | Status | Score | CTC / Details |",
            "|-----------|--------|-------|---------------|",
        ]
        pos_candidates = sorted(
            grouped[pos["id"]],
            key=lambda c: (
                ["Hired", "Primary", "Backup", "Optional", "On Hold",
                 "Excluded", "Rejected", "Withdrawn", "Backed Out"].index(c["status"])
                if c["status"] in
                ["Hired", "Primary", "Backup", "Optional", "On Hold",
                 "Excluded", "Rejected", "Withdrawn", "Backed Out"]
                else 99,
                -(c["score"] or 0),
            ),
        )
        for c in pos_candidates:
            lines.append(render_candidate_row(c))
        lines.append("")

    # Upcoming joining dates
    upcoming = [
        c for c in candidates
        if c.get("joining_date") and days_until(c["joining_date"]) >= 0
    ]
    upcoming.sort(key=lambda c: c["joining_date"])
    if upcoming:
        lines += ["---", "", "## Upcoming Joining Dates", ""]
        for c in upcoming:
            delta = days_until(c["joining_date"])
            lines.append(
                f"- **{c['name']}** — {c['joining_date']} "
                f"({'today' if delta == 0 else f'in {delta} days'})"
            )
        lines.append("")

    lines += [
        "---",
        "",
        f"_Report auto-generated daily at 10:00 AM IST. "
        f"Edit `candidates.json` to update pipeline data._",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
        return 1
    data = load_data()
    report = generate_report(data)
    OUTPUT_FILE.write_text(report)
    print(f"Report written to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
