#!/usr/bin/env python3
"""Generate daily candidate pipeline status report for Moolchand Healthcare Group."""

import json
import sys
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "candidates_data.json"
OUTPUT_FILE = Path(__file__).parent / "DAILY_STATUS_REPORT.md"

STATUS_EMOJI = {
    "Hired": "✅",
    "Primary": "⭐",
    "Backup": "🔵",
    "Optional": "🟡",
    "On Hold": "⏸️",
    "Excluded": "⛔",
    "Rejected": "❌",
    "Withdrawn": "↩️",
    "Backed Out": "⚠️",
}

URGENCY_EMOJI = {
    "CRITICAL": "🔴",
    "CRITICAL - NO BACKUP": "🚨",
    "URGENT": "🟠",
    "ON TRACK": "🟢",
}


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def get_urgency_icon(urgency: str) -> str:
    for key, icon in URGENCY_EMOJI.items():
        if urgency.startswith(key):
            return icon
    return "⚪"


def count_all_statuses(data: dict) -> dict:
    counts: dict[str, int] = {}
    for pos in data["positions"]:
        for c in pos["candidates"]:
            s = c["status"]
            counts[s] = counts.get(s, 0) + 1
    for c in data.get("additional_candidates", []):
        s = c["status"]
        counts[s] = counts.get(s, 0) + 1
    return counts


def total_candidates(data: dict) -> int:
    n = sum(len(p["candidates"]) for p in data["positions"])
    n += len(data.get("additional_candidates", []))
    return n


def positions_filled(data: dict) -> tuple[int, int]:
    hired = sum(p["hired_count"] for p in data["positions"])
    total = sum(p["target_headcount"] for p in data["positions"])
    return hired, total


def get_priority_actions(data: dict) -> list[dict]:
    actions = []
    for pos in data["positions"]:
        for c in pos["candidates"]:
            if c.get("priority") and c.get("action"):
                actions.append({
                    "priority": c["priority"],
                    "name": c["name"],
                    "position": pos["title"],
                    "action": c["action"],
                    "email": c.get("email"),
                    "phone": c.get("phone"),
                    "contact_via": c.get("contact_via"),
                    "offer": c.get("target_offer"),
                    "risk": c.get("risk"),
                })
    actions.sort(key=lambda x: x["priority"])
    return actions


def render_candidate_row(c: dict) -> str:
    icon = STATUS_EMOJI.get(c["status"], "•")
    score = f" · {c['score']}/10" if c.get("score") else ""
    ctc = ""
    if c.get("target_offer"):
        ctc = f" · Offer: ₹{c['target_offer']}"
    elif c.get("current_ctc"):
        ctc = f" · CTC: ₹{c['current_ctc']}"
    start = f" · Start: {c['estimated_start']}" if c.get("estimated_start") else ""
    join = f" · Joins: {c['joining_date']}" if c.get("joining_date") else ""
    contact = ""
    if c.get("email") or c.get("phone"):
        parts = []
        if c.get("email"):
            parts.append(c["email"])
        if c.get("phone"):
            parts.append(c["phone"])
        contact = f" · 📞 {' / '.join(parts)}"
    action_note = f"\n    → **{c['action']}**" if c.get("action") else ""
    reject_note = f" · _{c.get('rejection_reason', c.get('notes', ''))}_" if c["status"] in ("Rejected", "Backed Out", "Excluded", "Withdrawn") else ""
    return f"  {icon} **{c['name']}** ({c['id']}){score}{ctc}{start}{join}{contact}{reject_note}{action_note}"


def generate_report(data: dict) -> str:
    today = date.today()
    now = datetime.now().strftime("%I:%M %p")
    lines: list[str] = []

    lines.append(f"# Daily Hiring Pipeline Status")
    lines.append(f"**{data['organization']}** · Hiring Manager: {data['hiring_manager']}")
    lines.append(f"**Date:** {today.strftime('%B %d, %Y')} · **Generated:** {now} IST")
    lines.append(f"**Source Data Last Updated:** {data['last_updated']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive summary table
    filled, total_pos = positions_filled(data)
    remaining = total_pos - filled
    statuses = count_all_statuses(data)
    total = total_candidates(data)

    lines.append("## Pipeline Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Open Positions** | {total_pos} |")
    lines.append(f"| **Positions Filled** | {filled} / {total_pos} |")
    lines.append(f"| **Still Needed** | {remaining} |")
    lines.append(f"| **Total Candidates Tracked** | {total} |")
    lines.append(f"| **Hired** | {statuses.get('Hired', 0)} |")
    lines.append(f"| **Active Primaries** | {statuses.get('Primary', 0)} |")
    lines.append(f"| **Backups Available** | {statuses.get('Backup', 0)} |")
    lines.append(f"| **Rejected / Excluded** | {statuses.get('Rejected', 0) + statuses.get('Excluded', 0)} |")
    lines.append(f"| **Estimated Total CTC** | ₹{data['cost_summary']['total_estimated']} |")
    lines.append("")

    # Priority actions
    actions = get_priority_actions(data)
    if actions:
        lines.append("## Today's Priority Actions")
        lines.append("")
        for a in actions:
            contact_info = ""
            if a.get("email") or a.get("phone"):
                parts = []
                if a.get("email"):
                    parts.append(a["email"])
                if a.get("phone"):
                    parts.append(a["phone"])
                contact_info = f" · {' / '.join(parts)}"
            elif a.get("contact_via"):
                contact_info = f" · Via: {a['contact_via']}"
            offer_info = f" · Offer: ₹{a['offer']}" if a.get("offer") else ""
            risk_info = f"\n   > ⚠️ {a['risk']}" if a.get("risk") else ""
            lines.append(f"**P{a['priority']}** — {a['name']} ({a['position']}){contact_info}{offer_info}")
            lines.append(f"   _{a['action']}_")
            if a.get("risk"):
                lines.append(f"   > ⚠️ {a['risk']}")
            lines.append("")

    # Per-position breakdown
    lines.append("---")
    lines.append("")
    lines.append("## Position Details")
    lines.append("")

    for pos in data["positions"]:
        urgency_icon = get_urgency_icon(pos["urgency"])
        need = pos["target_headcount"] - pos["hired_count"]
        lines.append(f"### {urgency_icon} {pos['title']} ({pos['id']})")
        lines.append(
            f"**Target:** {pos['target_headcount']} · "
            f"**Hired:** {pos['hired_count']} · "
            f"**Still Needed:** {need} · "
            f"**Status:** {pos['urgency']}"
        )
        lines.append("")

        by_status: dict[str, list] = {}
        for c in pos["candidates"]:
            by_status.setdefault(c["status"], []).append(c)

        display_order = ["Hired", "Primary", "Backup", "Optional", "On Hold", "Backed Out", "Excluded", "Rejected", "Withdrawn"]
        for status in display_order:
            candidates = by_status.get(status, [])
            if not candidates:
                continue
            lines.append(f"**{status}**")
            for c in candidates:
                lines.append(render_candidate_row(c))
            lines.append("")

    # Joining timeline
    lines.append("---")
    lines.append("")
    lines.append("## Joining Timeline")
    lines.append("")
    for milestone, description in data["hiring_timeline"].items():
        # Highlight past dates
        try:
            milestone_date = datetime.strptime(milestone, "%Y-%m-%d").date() if "-" not in milestone[:4] else None
        except ValueError:
            milestone_date = None
        marker = "✅" if milestone_date and milestone_date <= today else "📅"
        lines.append(f"- {marker} **{milestone}** — {description}")
    lines.append("")

    # Cost summary
    lines.append("---")
    lines.append("")
    lines.append("## Cost Summary")
    lines.append("")
    lines.append("**Committed Hires**")
    lines.append("")
    lines.append("| Name | Position | CTC | Status |")
    lines.append("|------|----------|-----|--------|")
    for h in data["cost_summary"]["committed"]:
        lines.append(f"| {h['name']} | {h['position']} | ₹{h['ctc']} | {h['status']} |")
    lines.append("")
    lines.append("**Estimated (Pending Offers)**")
    lines.append("")
    lines.append("| Name | Position | CTC |")
    lines.append("|------|----------|-----|")
    for e in data["cost_summary"]["estimated"]:
        lines.append(f"| {e['name']} | {e['position']} | ₹{e['ctc']} |")
    lines.append(f"| | **TOTAL** | **₹{data['cost_summary']['total_estimated']}** |")
    lines.append("")
    lines.append(f"> **Premium scenario:** {data['cost_summary']['premium_scenario_addition']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Auto-generated at 10:00 AM IST · {today} · Edit `candidates_data.json` to update candidate records_")

    return "\n".join(lines)


def main() -> None:
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found", file=sys.stderr)
        sys.exit(1)

    data = load_data()
    report = generate_report(data)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
