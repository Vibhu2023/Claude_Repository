#!/usr/bin/env python3
"""Daily hiring pipeline status report generator.

Reads candidates.json and writes PIPELINE_STATUS.md with today's snapshot.
Run at 10 AM IST via GitHub Actions (cron: '30 4 * * *').
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).parent / "candidates.json"
OUTPUT_FILE = Path(__file__).parent / "PIPELINE_STATUS.md"

IST = timezone(timedelta(hours=5, minutes=30))

STATUS_PRIORITY = ["HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD",
                   "DECLINED_OFFER", "REJECTED", "BACKED_OUT",
                   "WITHDRAWN", "EXCLUDED", "DO_NOT_SEND"]

STATUS_EMOJI = {
    "HIRED":         "✅",
    "PRIMARY":       "🎯",
    "BACKUP":        "📋",
    "OPTIONAL":      "💡",
    "ON_HOLD":       "⏸️",
    "DECLINED_OFFER":"❌",
    "REJECTED":      "🚫",
    "BACKED_OUT":    "⚠️",
    "WITHDRAWN":     "🔙",
    "EXCLUDED":      "⛔",
    "DO_NOT_SEND":   "🔴",
}

URGENCY_BADGE = {
    "CRITICAL": "🔴 CRITICAL",
    "URGENT":   "🟠 URGENT",
    "NORMAL":   "🟢 NORMAL",
}


def load_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def count_by_status(candidates: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in candidates:
        s = c["status"]
        counts[s] = counts.get(s, 0) + 1
    return counts


def candidates_needing_action(candidates: list[dict]) -> list[dict]:
    return [c for c in candidates
            if c.get("action_required") and c["status"] in ("PRIMARY", "HIRED")]


def render_report(data: dict, now: datetime) -> str:
    org = data["meta"]["organization"]
    mgr = data["meta"]["hiring_manager"]
    positions = data["positions"]
    candidates = data["candidates"]

    lines: list[str] = []
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p IST")

    lines += [
        f"# {org} — Hiring Pipeline Status",
        f"**Date:** {date_str} | **Generated:** {time_str}",
        f"**Hiring Manager:** {mgr}",
        "",
        "---",
        "",
    ]

    # ── Executive Summary ──────────────────────────────────────────────────
    lines.append("## Executive Summary\n")
    counts = count_by_status(candidates)
    total = len(candidates)
    lines += [
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total candidates tracked | {total} |",
        f"| ✅ Hired | {counts.get('HIRED', 0)} |",
        f"| 🎯 Active Primary | {counts.get('PRIMARY', 0)} |",
        f"| 📋 Backup | {counts.get('BACKUP', 0)} |",
        f"| 💡 Optional | {counts.get('OPTIONAL', 0)} |",
        f"| ⏸️ On Hold | {counts.get('ON_HOLD', 0)} |",
        f"| ❌ Declined / Rejected / Backed Out | "
        f"{counts.get('DECLINED_OFFER', 0) + counts.get('REJECTED', 0) + counts.get('BACKED_OUT', 0)} |",
        "",
    ]

    # ── Actions needed today ───────────────────────────────────────────────
    urgent = candidates_needing_action(candidates)
    if urgent:
        lines.append("## ⚡ Actions Required Today\n")
        for c in urgent:
            emoji = STATUS_EMOJI.get(c["status"], "")
            lines.append(f"- {emoji} **{c['name']}** ({c['position_title']}) — "
                         f"{c['action_required']}")
            if c.get("email"):
                lines.append(f"  - Email: {c['email']}")
            if c.get("phone"):
                lines.append(f"  - Phone: {c['phone']}")
            if c.get("target_offer"):
                lines.append(f"  - Offer: {c['target_offer']}")
            if c.get("est_start"):
                lines.append(f"  - Est. Start: {c['est_start']}")
        lines.append("")

    # ── Per-position breakdown ─────────────────────────────────────────────
    lines.append("## Position Breakdown\n")
    pos_map = {p["id"]: p for p in positions}
    from collections import defaultdict
    by_pos: dict[str, list[dict]] = defaultdict(list)
    for c in candidates:
        by_pos[c["position_id"]].append(c)

    for pos in positions:
        pid = pos["id"]
        urgency = URGENCY_BADGE.get(pos.get("urgency", "NORMAL"), pos.get("urgency", ""))
        hired = pos["hired"]
        needed = pos["needed"]
        target = pos["target_headcount"]

        progress = "█" * hired + "░" * needed
        lines += [
            f"### {pos['title']} ({pid})",
            f"**Status:** {urgency} | "
            f"**Progress:** {progress} {hired}/{target} filled | "
            f"**Still need:** {needed}",
            "",
        ]

        pos_candidates = sorted(
            by_pos.get(pid, []),
            key=lambda c: STATUS_PRIORITY.index(c["status"])
            if c["status"] in STATUS_PRIORITY else 99
        )

        lines.append("| Candidate | Status | Score | Action |")
        lines.append("|-----------|--------|-------|--------|")
        for c in pos_candidates:
            emoji = STATUS_EMOJI.get(c["status"], "")
            score = f"{c['score']}/10" if c.get("score") else "—"
            action = c.get("action_required") or "—"
            deadline = c.get("action_deadline")
            if deadline:
                action = f"{action} *(by {deadline})*"
            lines.append(
                f"| **{c['name']}** | {emoji} {c['status']} | {score} | {action} |"
            )
        lines.append("")

    # ── Full candidate detail for primaries ────────────────────────────────
    primaries = [c for c in candidates if c["status"] == "PRIMARY"]
    if primaries:
        lines.append("## Primary Candidate Detail\n")
        for c in primaries:
            lines.append(f"### {c['name']} — {c['position_title']}")
            if c.get("score"):
                lines.append(f"- **Score:** {c['score']}/10")
            if c.get("source"):
                lines.append(f"- **Source:** {c['source']}")
            if c.get("current_ctc"):
                lines.append(f"- **Current CTC:** {c['current_ctc']}")
            if c.get("target_offer"):
                lines.append(f"- **Target Offer:** {c['target_offer']}")
            if c.get("notice_days") is not None:
                lines.append(f"- **Notice Period:** {c['notice_days']} days")
            if c.get("est_start"):
                lines.append(f"- **Est. Start:** {c['est_start']}")
            if c.get("email"):
                lines.append(f"- **Email:** {c['email']}")
            if c.get("phone"):
                lines.append(f"- **Phone:** {c['phone']}")
            if c.get("location"):
                lines.append(f"- **Location:** {c['location']}")
            if c.get("contact_via"):
                lines.append(f"- **Contact Via:** {c['contact_via']}")
            if c.get("notes"):
                lines.append(f"- **Notes:** {c['notes']}")
            if c.get("action_required"):
                lines.append(f"- **Action:** {c['action_required']}")
            lines.append("")

    # ── Footer ─────────────────────────────────────────────────────────────
    lines += [
        "---",
        "",
        f"*Auto-generated daily at 10:00 AM IST. Source: `candidates.json`.*",
        f"*Last data update: {data['meta']['last_updated']}*",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
        sys.exit(1)

    data = load_data()
    now = datetime.now(IST)
    report = render_report(data, now)

    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Pipeline status written to {OUTPUT_FILE}")
    print(report)


if __name__ == "__main__":
    main()
