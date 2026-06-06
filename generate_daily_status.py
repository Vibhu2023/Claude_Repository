#!/usr/bin/env python3
"""Generate daily pipeline status report and write to DAILY_STATUS.md."""

from datetime import datetime, timezone, timedelta
from collections import defaultdict
from candidates_data import CANDIDATES, POSITIONS, STATUS_LABELS, ACTIVE_STATUSES

IST = timezone(timedelta(hours=5, minutes=30))


def _section(title: str, level: int = 2) -> str:
    return f"\n{'#' * level} {title}\n"


def generate_report() -> str:
    now = datetime.now(IST)
    lines = []

    lines.append("# Moolchand Healthcare Group — Daily Pipeline Status")
    lines.append(f"**Report Date:** {now.strftime('%B %d, %Y')}  ")
    lines.append(f"**Generated:** {now.strftime('%I:%M %p IST')}  ")
    lines.append(f"**Hiring Manager:** Vibhu Talwar\n")
    lines.append("---")

    # ── Summary counts ─────────────────────────────────────────────────
    counts: dict[str, int] = defaultdict(int)
    for c in CANDIDATES:
        counts[c["status"]] += 1

    lines.append(_section("Executive Summary"))
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total Positions** | {len(POSITIONS)} |")
    lines.append(f"| **Total Candidates** | {len(CANDIDATES)} |")
    for status, label in STATUS_LABELS.items():
        if counts[status]:
            lines.append(f"| **{label}** | {counts[status]} |")

    # Determine overall health
    primaries = [c for c in CANDIDATES if c["status"] == "PRIMARY"]
    hired = [c for c in CANDIDATES if c["status"] == "HIRED"]
    no_backup_positions = []
    for pos_id in POSITIONS:
        has_backup = any(
            c["position"] == pos_id and c["status"] in ("BACKUP", "OPTIONAL")
            for c in CANDIDATES
        )
        has_primary = any(
            c["position"] == pos_id and c["status"] == "PRIMARY"
            for c in CANDIDATES
        )
        if has_primary and not has_backup:
            no_backup_positions.append(POSITIONS[pos_id])

    if no_backup_positions:
        health = "CRITICAL — no backup for: " + ", ".join(no_backup_positions)
    elif len(primaries) < len(POSITIONS) - len(hired):
        health = "AT RISK — some positions have no primary candidate"
    else:
        health = "ON TRACK"

    lines.append(f"\n**Overall Pipeline Health:** {health}\n")
    lines.append("---")

    # ── Per-position breakdown ─────────────────────────────────────────
    lines.append(_section("Position Breakdown"))

    for pos_id, pos_name in POSITIONS.items():
        pos_candidates = [c for c in CANDIDATES if c["position"] == pos_id]
        pos_hired = [c for c in pos_candidates if c["status"] == "HIRED"]
        lines.append(_section(f"{pos_name} ({pos_id})", level=3))
        lines.append(f"**Hired:** {len(pos_hired)} | **Need:** TBD\n")
        lines.append("| Candidate | Status | Score | CTC | Action |")
        lines.append("|-----------|--------|-------|-----|--------|")
        for c in sorted(pos_candidates, key=lambda x: (
            list(STATUS_LABELS).index(x["status"]) if x["status"] in STATUS_LABELS else 99,
            -x["score"],
        )):
            label = STATUS_LABELS.get(c["status"], c["status"])
            score_str = f"{c['score']}/10" if c["score"] else "—"
            ctc_str = c["ctc"] or "—"
            action_str = c["action"] or "—"
            lines.append(
                f"| {c['name']} | {label} | {score_str} | {ctc_str} | {action_str} |"
            )

    lines.append("\n---")

    # ── Today's action items ───────────────────────────────────────────
    lines.append(_section("Today's Action Items"))
    active_with_actions = [
        c for c in CANDIDATES if c["status"] in ACTIVE_STATUSES and c["action"]
    ]
    if active_with_actions:
        for i, c in enumerate(active_with_actions, 1):
            contact_info = ""
            if c["contact"]:
                contact_info += f" · {c['contact']}"
            if c["phone"]:
                contact_info += f" · {c['phone']}"
            lines.append(
                f"{i}. **[{STATUS_LABELS[c['status']]}] {c['name']}** ({POSITIONS[c['position']]})"
            )
            lines.append(f"   - {c['action']}{contact_info}")
    else:
        lines.append("_No pending actions._")

    lines.append("\n---")

    # ── Upcoming joiners ───────────────────────────────────────────────
    lines.append(_section("Upcoming Joiners"))
    joiners = [c for c in CANDIDATES if c.get("joining_date") and c["status"] in ("HIRED", "PRIMARY")]
    if joiners:
        joiners_sorted = sorted(joiners, key=lambda x: x["joining_date"])
        lines.append("| Candidate | Position | Joining Date | Status |")
        lines.append("|-----------|----------|--------------|--------|")
        for c in joiners_sorted:
            label = STATUS_LABELS.get(c["status"], c["status"])
            lines.append(
                f"| {c['name']} | {POSITIONS[c['position']]} | {c['joining_date']} | {label} |"
            )
    else:
        lines.append("_No confirmed joiners yet._")

    lines.append("\n---")
    lines.append(f"_Auto-generated daily at 10:00 AM IST. Edit `candidates_data.py` to update statuses._")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    report = generate_report()
    output_path = "DAILY_STATUS.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {output_path}")
