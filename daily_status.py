"""
Daily pipeline status generator for Moolchand Healthcare Group hiring pipeline.
Reads HIRING_PIPELINE_REPORT.md and writes a dated snapshot to DAILY_STATUS.md.
"""

import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST).strftime("%B %d, %Y")
TODAY_SHORT = datetime.now(IST).strftime("%Y-%m-%d")

REPORT_FILE = Path("HIRING_PIPELINE_REPORT.md")
STATUS_FILE = Path("DAILY_STATUS.md")
LOG_FILE = Path("STATUS_LOG.md")


def extract_section(text, header):
    pattern = rf"(?:^|\n)(#{1,3} {re.escape(header)}.*?)(?=\n#{1,3} |\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_exec_summary(text):
    rows = re.findall(r"\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|", text)
    return {k.strip(): v.strip() for k, v in rows}


def parse_candidate_statuses(text):
    """Extract each position's top candidates and their current status."""
    positions = []

    # Finance Manager
    fin = {"name": "Sr Finance Manager (FIN-001)", "candidates": []}
    if "Jatin Sachdeva" in text:
        fin["candidates"].append("✅ Jatin Sachdeva — HIRED (joins June 18, 2026)")
    if "CA Rahul Madaan" in text:
        fin["candidates"].append("🎯 CA Rahul Madaan — PRIMARY (Score 8.8/10, target ₹42-44L)")
    if "Backed Out" not in text or "FIN" not in text:
        fin["candidates"].append("📋 Backups: Manu Singla, Jatin Anand, Kapil Sharma, Ritu Arora, Shukla Satia")
    positions.append(fin)

    # RPA Developer
    rpa = {"name": "RPA Developer (RPA-001)", "candidates": []}
    if "Ritik Gupta" in text and "BACKED OUT" in text.upper():
        rpa["candidates"].append("⚠️  Ritik Gupta — BACKED OUT (was hired)")
    if "Kamal" in text and "RPA-KAM" in text:
        rpa["candidates"].append("🎯 Kamal — PRIMARY #1 (Score 7.8/10, ₹6.6L, 90-day notice)")
    if "Anshul Vashisth" in text:
        rpa["candidates"].append("🎯 Anshul Vashisth — PRIMARY #2 (Score 8.8/10, ₹6L + training)")
    if "Shahe Faisal" in text:
        rpa["candidates"].append("💎 Shahe Faisal — OPTIONAL PREMIUM (Score 8.5/10, ₹13-15L)")
    positions.append(rpa)

    # DRO
    dro = {"name": "Chief Digital Revenue Officer (DRO-001)", "candidates": []}
    if "Kuwarjeet Sidana" in text:
        dro["candidates"].append("🎯 Kuwarjeet Sidana — ONLY CANDIDATE (Score 9.5/10, ₹28L)")
        dro["candidates"].append("🚨 NO BACKUP — must close urgently")
    positions.append(dro)

    return positions


def parse_priority_actions(text):
    """Extract the current priority action items."""
    actions = []
    items = re.findall(
        r"### PRIORITY (\d+)[^\n]*\n(.*?)(?=### PRIORITY|\n---|\Z)", text, re.DOTALL
    )
    for priority, block in items:
        contact = re.search(r"\*\*Contact:\*\*\s*(.+?)(?:\n|$)", block)
        confirm = re.search(r"\*\*Confirm:\*\*\s*(.+?)(?:\n|$)", block)
        timeline = re.search(r"\*\*Timeline:\*\*\s*(.+?)(?:\n|$)", block)
        person = contact or confirm
        if person:
            tl = f" — {timeline.group(1).strip()}" if timeline else ""
            actions.append(f"Priority {priority}: {person.group(1).strip()}{tl}")
    return actions


def build_status_report(report_text):
    metrics = parse_exec_summary(report_text)
    positions = parse_candidate_statuses(report_text)
    actions = parse_priority_actions(report_text)

    lines = [
        f"# Daily Pipeline Status — {TODAY}",
        f"**Generated:** {TODAY} at 10:00 AM IST  ",
        f"**Hiring Manager:** Vibhu Talwar  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Current Status |",
        "|--------|----------------|",
    ]

    metric_keys = [
        "Total Open Positions", "Total Candidates", "Hired",
        "Active Candidates (Primary)", "Backup Candidates",
        "Rejected/Excluded", "Cost Estimate (Remaining 4)"
    ]
    for k in metric_keys:
        if k in metrics:
            lines.append(f"| **{k}** | {metrics[k]} |")

    lines += [
        "",
        "---",
        "",
        "## Candidate Status by Position",
        "",
    ]

    for pos in positions:
        lines.append(f"### {pos['name']}")
        for c in pos["candidates"]:
            lines.append(f"- {c}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Pending Actions",
        "",
    ]
    if actions:
        for a in actions:
            lines.append(f"- {a}")
    else:
        lines.append("_No structured priority actions found — review pipeline report._")

    lines += [
        "",
        "---",
        "",
        f"_Auto-generated daily at 10:00 AM IST. Source: `HIRING_PIPELINE_REPORT.md`_",
    ]

    return "\n".join(lines)


def append_to_log(status_summary):
    """Append a one-liner entry to STATUS_LOG.md for historical tracking."""
    header_needed = not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0
    with LOG_FILE.open("a") as f:
        if header_needed:
            f.write("# Pipeline Status Log\n\n")
            f.write("| Date | Hired | Primary | Pending Actions |\n")
            f.write("|------|-------|---------|------------------|\n")

        hired_match = re.search(r"\*\*Hired\*\*\s*\|\s*(\d+)", status_summary)
        primary_match = re.search(r"\*\*Active Candidates \(Primary\)\*\*\s*\|\s*(\d+)", status_summary)
        action_count = status_summary.count("Priority")

        hired = hired_match.group(1) if hired_match else "?"
        primary = primary_match.group(1) if primary_match else "?"
        f.write(f"| {TODAY_SHORT} | {hired} | {primary} | {action_count} open priorities |\n")


def main():
    if not REPORT_FILE.exists():
        print(f"ERROR: {REPORT_FILE} not found.")
        return 1

    report_text = REPORT_FILE.read_text(encoding="utf-8")
    status = build_status_report(report_text)

    STATUS_FILE.write_text(status, encoding="utf-8")
    print(f"Written: {STATUS_FILE}")

    append_to_log(status)
    print(f"Appended: {LOG_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
