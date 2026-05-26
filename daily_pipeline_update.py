#!/usr/bin/env python3
"""Daily hiring pipeline status report generator - runs at 10 AM IST."""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


IST = timezone(timedelta(hours=5, minutes=30))

STATUS_EMOJI = {
    "HIRED":      "✅",
    "PRIMARY":    "🎯",
    "BACKUP":     "🔄",
    "OPTIONAL":   "💡",
    "ON_HOLD":    "⏸️",
    "DECLINED":   "❌",
    "REJECTED":   "🚫",
    "WITHDRAWN":  "↩️",
    "BACKED_OUT": "⚠️",
    "EXCLUDED":   "⛔",
}

ACTIVE_STATUSES = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD"}


def load_data(path: str = "pipeline_data.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


def count_by_status(candidates: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for c in candidates:
        s = c["status"]
        counts[s] = counts.get(s, 0) + 1
    return counts


def positions_summary(data: dict) -> str:
    positions = data["positions"]
    candidates = data["candidates"]
    lines = []
    for pos_id, pos in positions.items():
        hired = sum(
            1 for c in candidates
            if c["position"] == pos_id and c["status"] == "HIRED"
        )
        primaries = [
            c for c in candidates
            if c["position"] == pos_id and c["status"] == "PRIMARY"
        ]
        need = pos["target"] - hired
        status_icon = "✅" if need == 0 else ("🔴" if need > 0 and not primaries else "🟡")
        lines.append(
            f"  {status_icon} **{pos['title']}** ({pos_id}): "
            f"{hired}/{pos['target']} hired | {need} still needed"
        )
        for p in primaries:
            score_str = f" [{p['score']}/10]" if p.get("score") else ""
            lines.append(f"       → {p['name']}{score_str} — {p.get('notes', '')}")
    return "\n".join(lines)


def active_candidates_table(data: dict) -> str:
    candidates = [c for c in data["candidates"] if c["status"] in ACTIVE_STATUSES]
    positions = data["positions"]

    header = f"{'Name':<25} {'Position':<12} {'Status':<12} {'Score':>6} {'Offer':>12} {'Start':>12}"
    sep = "-" * len(header)
    rows = [header, sep]
    for c in candidates:
        pos_title = positions.get(c["position"], {}).get("title", c["position"])[:11]
        score = f"{c['score']}/10" if c.get("score") else "  N/A"
        offer = c.get("target_offer", c.get("offer_ctc", "TBD"))
        start = c.get("joining_date", c.get("est_start", "TBD"))
        emoji = STATUS_EMOJI.get(c["status"], "")
        rows.append(
            f"{c['name']:<25} {pos_title:<12} {emoji} {c['status']:<10} {score:>6} {offer:>12} {start:>12}"
        )
    return "\n".join(rows)


def todays_actions(data: dict) -> str:
    actions = data.get("daily_actions", {})
    lines = []
    for priority_key in sorted(actions):
        block = actions[priority_key]
        lines.append(f"\n  **{block['label']}**")
        for item in block["items"]:
            lines.append(f"    • {item}")
    return "\n".join(lines)


def generate_report(data: dict, as_of: datetime) -> str:
    meta = data["meta"]
    candidates = data["candidates"]
    counts = count_by_status(candidates)

    total = len(candidates)
    active = sum(counts.get(s, 0) for s in ACTIVE_STATUSES)
    hired = counts.get("HIRED", 0)
    primary = counts.get("PRIMARY", 0)
    backup = counts.get("BACKUP", 0)
    rejected_out = sum(counts.get(s, 0) for s in ("DECLINED", "REJECTED", "WITHDRAWN", "BACKED_OUT", "EXCLUDED"))

    date_str = as_of.strftime("%B %d, %Y")
    time_str = as_of.strftime("%I:%M %p IST")

    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║         DAILY HIRING PIPELINE STATUS — {date_str:<24}║
║         {meta['org']:<57}║
║         Hiring Manager: {meta['hiring_manager']:<38}║
╚══════════════════════════════════════════════════════════════════╝
Generated: {time_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PIPELINE SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Candidates : {total}
  Active           : {active}  (Hired + Primary + Backup + Optional)
    ✅  Hired      : {hired}
    🎯  Primary    : {primary}
    🔄  Backup     : {backup}
  Rejected/Out     : {rejected_out}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSITIONS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{positions_summary(data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE CANDIDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{active_candidates_table(data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION ITEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{todays_actions(data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data last manually updated: {data['meta']['last_updated']}
Next automated report: Tomorrow 10:00 AM IST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
    return report


def save_report(report: str, as_of: datetime) -> Path:
    reports_dir = Path("pipeline_reports")
    reports_dir.mkdir(exist_ok=True)
    filename = reports_dir / f"status_{as_of.strftime('%Y-%m-%d')}.txt"
    filename.write_text(report + "\n")
    return filename


def main() -> None:
    data_path = "pipeline_data.json"
    if not Path(data_path).exists():
        print(f"ERROR: {data_path} not found.", file=sys.stderr)
        sys.exit(1)

    data = load_data(data_path)
    now_ist = datetime.now(IST)
    report = generate_report(data, now_ist)

    print(report)

    saved = save_report(report, now_ist)
    print(f"\n[Report saved to {saved}]")


if __name__ == "__main__":
    main()
