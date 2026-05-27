#!/usr/bin/env python3
"""Generate a daily 10 AM pipeline status report from candidates.json."""

import json
import sys
from datetime import date, datetime
from pathlib import Path


STATUS_PRIORITY = {
    "HIRED": 0,
    "PRIMARY": 1,
    "OPTIONAL": 2,
    "BACKUP": 3,
    "ON_HOLD": 4,
    "BACKED_OUT": 5,
    "DO_NOT_SEND": 6,
    "REJECTED": 7,
}

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🎯",
    "OPTIONAL": "💡",
    "BACKUP": "🔄",
    "ON_HOLD": "⏸️",
    "BACKED_OUT": "❌",
    "DO_NOT_SEND": "🚫",
    "REJECTED": "❌",
}


def load_data(path: str = "candidates.json") -> dict:
    with open(path) as f:
        return json.load(f)


def days_until(date_str: str) -> int | None:
    try:
        target = date.fromisoformat(date_str)
        return (target - date.today()).days
    except (ValueError, TypeError):
        return None


def format_ctc(ctc: str) -> str:
    return f"₹{ctc}" if ctc else "N/A"


def build_report(data: dict) -> str:
    today = datetime.now().strftime("%B %d, %Y")
    now_time = datetime.now().strftime("%I:%M %p")
    lines = []

    lines.append(f"# Daily Hiring Pipeline Status")
    lines.append(f"**{data['organization']}** | Generated: {today} at {now_time}")
    lines.append(f"**Hiring Manager:** {data['hiring_manager']}")
    lines.append("")

    # --- Executive Summary ---
    total_target = sum(p["target_hires"] for p in data["positions"])
    total_hired = sum(p["hired_count"] for p in data["positions"])
    all_candidates = [c for p in data["positions"] for c in p["candidates"]]
    primaries = [c for c in all_candidates if c["status"] == "PRIMARY"]
    backups = [c for c in all_candidates if c["status"] == "BACKUP"]

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Open Positions | {total_target} |")
    lines.append(f"| Hired | {total_hired} / {total_target} |")
    lines.append(f"| Remaining to Fill | {total_target - total_hired} |")
    lines.append(f"| Active Primary Candidates | {len(primaries)} |")
    lines.append(f"| Backup Candidates | {len(backups)} |")
    lines.append("")

    # --- Position-by-Position ---
    lines.append("## Position Status")
    lines.append("")

    for pos in data["positions"]:
        need = pos["target_hires"] - pos["hired_count"]
        urgency = "🔴 URGENT" if need > 0 else "🟢 FILLED"
        lines.append(f"### {pos['title']} ({pos['id']})")
        lines.append(
            f"**Target:** {pos['target_hires']} | **Hired:** {pos['hired_count']} | **Need:** {need} | {urgency}"
        )
        lines.append("")

        sorted_candidates = sorted(
            pos["candidates"], key=lambda c: STATUS_PRIORITY.get(c["status"], 99)
        )

        for c in sorted_candidates:
            emoji = STATUS_EMOJI.get(c["status"], "")
            score = f" | Score: {c['score']}/10" if c.get("score") else ""
            lines.append(f"#### {emoji} {c['name']} — `{c['status']}`{score}")

            if c.get("action"):
                lines.append(f"> **ACTION:** {c['action']}")

            details = []
            if c.get("target_offer"):
                details.append(f"Offer: {format_ctc(c['target_offer'])}")
            if c.get("notice_days") is not None:
                details.append(f"Notice: {c['notice_days']} days")
            if c.get("est_start"):
                details.append(f"Est. Start: {c['est_start']}")
            if c.get("joining_date"):
                days = days_until(c["joining_date"])
                joining_str = f"Joining: {c['joining_date']}"
                if days is not None:
                    joining_str += f" ({days} days away)"
                details.append(joining_str)
            if c.get("email"):
                details.append(f"Email: {c['email']}")
            if c.get("phone"):
                details.append(f"Phone: {c['phone']}")

            if details:
                lines.append(" | ".join(details))

            if c.get("notes"):
                lines.append(f"*{c['notes']}*")

            lines.append("")

    # --- Action Items ---
    lines.append("## Today's Action Items")
    lines.append("")
    action_count = 0
    for pos in data["positions"]:
        for c in pos["candidates"]:
            if c["status"] == "PRIMARY" and c.get("action"):
                action_count += 1
                contact = ""
                if c.get("email"):
                    contact += f" | Email: {c['email']}"
                if c.get("phone"):
                    contact += f" | Phone: {c['phone']}"
                if c.get("contact_via"):
                    contact += f" | Via: {c['contact_via']}"
                lines.append(f"{action_count}. **{c['name']}** ({pos['title']})")
                lines.append(f"   - Action: {c['action']}")
                if contact:
                    lines.append(f"   - Contact:{contact}")
                lines.append("")

    # --- Joining Soon ---
    lines.append("## Joining Soon")
    lines.append("")
    joining_soon = [
        c for p in data["positions"] for c in p["candidates"]
        if c.get("joining_date") and c["status"] == "HIRED"
    ]
    if joining_soon:
        for c in joining_soon:
            days = days_until(c["joining_date"])
            days_str = f"**{days} days away**" if days is not None else ""
            lines.append(f"- **{c['name']}** → {c['joining_date']} {days_str}")
    else:
        lines.append("- No confirmed joiners yet.")
    lines.append("")

    lines.append("---")
    lines.append(
        f"*Report auto-generated daily at 10:00 AM IST from `candidates.json` | "
        f"Last data update: {data.get('last_updated', 'unknown')}*"
    )

    return "\n".join(lines)


def main() -> None:
    data_path = Path(__file__).parent / "candidates.json"
    if not data_path.exists():
        print("ERROR: candidates.json not found", file=sys.stderr)
        sys.exit(1)

    data = load_data(str(data_path))
    report = build_report(data)

    # Write to dated file and also overwrite DAILY_STATUS.md
    out_dir = Path(__file__).parent
    dated_name = f"pipeline_status_{date.today().isoformat()}.md"
    (out_dir / dated_name).write_text(report)
    (out_dir / "DAILY_STATUS.md").write_text(report)

    print(report)
    print(f"\n✓ Report written to {dated_name} and DAILY_STATUS.md", file=sys.stderr)


if __name__ == "__main__":
    main()
