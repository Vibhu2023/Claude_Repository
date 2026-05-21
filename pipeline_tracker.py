#!/usr/bin/env python3
"""Daily hiring pipeline status report generator."""

import json
import sys
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "candidates_data.json"
REPORT_FILE = Path(__file__).parent / "HIRING_PIPELINE_REPORT.md"

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🎯",
    "BACKUP": "🔄",
    "OPTIONAL": "⭐",
    "ON_HOLD": "⏸️",
    "REJECTED": "❌",
    "EXCLUDED": "🚫",
    "WITHDRAWN": "↩️",
    "BACKED_OUT": "⚠️",
}

# Maps status to urgency ordering for priority display
STATUS_ORDER = ["HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD",
                "EXCLUDED", "WITHDRAWN", "BACKED_OUT", "REJECTED"]


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data: dict) -> None:
    data["meta"]["last_updated"] = date.today().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_candidate_status(candidate_id: str, new_status: str, notes: str = "") -> bool:
    """Update a candidate's status in the data file."""
    data = load_data()
    valid_statuses = set(STATUS_EMOJI.keys())
    if new_status.upper() not in valid_statuses:
        print(f"Invalid status '{new_status}'. Valid: {sorted(valid_statuses)}")
        return False
    for c in data["candidates"]:
        if c["id"] == candidate_id:
            old_status = c.get("status", "UNKNOWN")
            c["status"] = new_status.upper()
            if notes:
                c["notes"] = notes
            save_data(data)
            print(f"Updated {c['name']} ({candidate_id}): {old_status} → {new_status.upper()}")
            return True
    print(f"Candidate ID '{candidate_id}' not found.")
    return False


def _count_by_status(candidates: list) -> dict:
    counts: dict = {}
    for c in candidates:
        s = c.get("status", "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1
    return counts


def _positions_by_id(data: dict) -> dict:
    return {pid: pos for pid, pos in data["positions"].items()}


def _candidates_for_position(candidates: list, position_id: str) -> list:
    return [c for c in candidates if c.get("position") == position_id]


def generate_report(data: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    now = datetime.now().strftime("%I:%M %p IST")
    candidates = data["candidates"]
    positions = _positions_by_id(data)
    counts = _count_by_status(candidates)

    total = len(candidates)
    active_primaries = counts.get("PRIMARY", 0)
    backups = counts.get("BACKUP", 0)
    hired = counts.get("HIRED", 0)
    rejected = counts.get("REJECTED", 0) + counts.get("BACKED_OUT", 0) + counts.get("WITHDRAWN", 0)

    lines = [
        f"# {data['meta']['organization']} – Hiring Pipeline Report",
        f"**Generated:** {today} at {now}  ",
        f"**Hiring Manager:** {data['meta']['hiring_manager']}  ",
        f"**Total Candidates:** {total}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Status |",
        "|--------|--------|",
        f"| **Total Open Positions** | {data['meta']['total_open_positions']} |",
        f"| **Total Candidates** | {total} |",
        f"| **Hired** | {hired} |",
        f"| **Active Candidates (Primary)** | {active_primaries} |",
        f"| **Backup Candidates** | {backups} |",
        f"| **Rejected / Withdrawn / Backed Out** | {rejected} |",
        "",
        "---",
        "",
        "## Position-wise Status",
        "",
    ]

    for pid, pos in positions.items():
        pos_candidates = _candidates_for_position(candidates, pid)
        pos_candidates_sorted = sorted(
            pos_candidates,
            key=lambda c: STATUS_ORDER.index(c.get("status", "REJECTED"))
            if c.get("status", "REJECTED") in STATUS_ORDER else 99,
        )

        filled = sum(1 for c in pos_candidates if c.get("status") == "HIRED")
        lines.append(f"### {pos['title']} ({pid})")
        lines.append(f"**Target:** {pos['target']} | **Hired:** {filled} | **Still Needed:** {pos['need']}")
        lines.append("")
        lines.append("| # | Candidate | Status | Score | Action / Notes |")
        lines.append("|---|-----------|--------|-------|----------------|")

        for c in pos_candidates_sorted:
            status = c.get("status", "UNKNOWN")
            emoji = STATUS_EMOJI.get(status, "")
            score = f"{c['score']}/10" if "score" in c else "—"
            action = c.get("action", c.get("notes", "—"))
            if len(action) > 60:
                action = action[:57] + "..."
            cid = c.get("id", "")
            lines.append(f"| {cid} | **{c['name']}** | {emoji} {status} | {score} | {action} |")

        lines.append("")

    # Immediate action items
    primaries = [c for c in candidates if c.get("status") == "PRIMARY"]
    if primaries:
        lines += [
            "---",
            "",
            "## Today's Action Items",
            "",
        ]
        for c in sorted(primaries, key=lambda x: x.get("priority", 99)):
            pos_title = positions.get(c.get("position", ""), {}).get("title", c.get("position", ""))
            lines.append(f"- **{c['name']}** ({pos_title})")
            if c.get("email"):
                lines.append(f"  - Email: {c['email']}")
            if c.get("phone"):
                lines.append(f"  - Phone: {c['phone']}")
            if c.get("target_ctc"):
                lines.append(f"  - Offer: ₹{c['target_ctc']}")
            if c.get("action"):
                lines.append(f"  - Action: {c['action']}")
            lines.append("")

    lines += [
        "---",
        "",
        "## Candidate Status Breakdown",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]
    for status in STATUS_ORDER:
        cnt = counts.get(status, 0)
        if cnt:
            emoji = STATUS_EMOJI.get(status, "")
            lines.append(f"| {emoji} **{status}** | {cnt} |")

    lines += [
        "",
        "---",
        "",
        f"**Last Updated:** {today}  ",
        f"**Report Generated For:** {data['meta']['hiring_manager']}",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "update":
        # Usage: python pipeline_tracker.py update <ID> <STATUS> [notes]
        if len(sys.argv) < 4:
            print("Usage: pipeline_tracker.py update <CANDIDATE_ID> <STATUS> [notes]")
            sys.exit(1)
        candidate_id = sys.argv[2]
        new_status = sys.argv[3]
        notes = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        success = update_candidate_status(candidate_id, new_status, notes)
        if not success:
            sys.exit(1)

    data = load_data()
    report = generate_report(data)
    REPORT_FILE.write_text(report)
    print(f"Report updated: {REPORT_FILE}")
    print(report[:500] + "\n... (truncated)")


if __name__ == "__main__":
    main()
