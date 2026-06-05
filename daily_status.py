#!/usr/bin/env python3
"""
Daily 10 AM Hiring Pipeline Status Report
Moolchand Healthcare Group
Run: python daily_status.py
Schedule: crontab -e  →  0 10 * * * cd /path/to/repo && python daily_status.py
"""

import json
import os
import sys
from datetime import date, datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "pipeline_data.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "status_reports")

# Terminal colour codes
R = "\033[91m"   # red
Y = "\033[93m"   # yellow
G = "\033[92m"   # green
B = "\033[94m"   # blue
W = "\033[97m"   # white / bold
C = "\033[96m"   # cyan
DIM = "\033[2m"
RESET = "\033[0m"

STATUS_COLOURS = {
    "HIRED":       G,
    "PRIMARY":     C,
    "BACKUP":      Y,
    "OPTIONAL":    B,
    "ON_HOLD":     Y,
    "REJECTED":    DIM,
    "EXCLUDED":    DIM,
    "WITHDRAWN":   DIM,
    "BACKED_OUT":  R,
    "DO_NOT_SEND": DIM,
}

STATUS_LABELS = {
    "HIRED":       "HIRED ✓",
    "PRIMARY":     "PRIMARY",
    "BACKUP":      "BACKUP",
    "OPTIONAL":    "OPTIONAL",
    "ON_HOLD":     "ON HOLD",
    "REJECTED":    "REJECTED",
    "EXCLUDED":    "EXCLUDED",
    "WITHDRAWN":   "WITHDRAWN",
    "BACKED_OUT":  "BACKED OUT",
    "DO_NOT_SEND": "DO NOT SEND",
}

ACTIVE_STATUSES = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD"}


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def parse_date(s):
    if s:
        return datetime.strptime(s, "%Y-%m-%d").date()
    return None


def days_diff(d):
    """Positive = overdue, negative = days remaining."""
    if d is None:
        return None
    return (date.today() - d).days


def urgency_tag(due_date_str):
    d = parse_date(due_date_str)
    if d is None:
        return ""
    diff = days_diff(d)
    if diff > 0:
        return f"{R}[OVERDUE {diff}d]{RESET}"
    if diff == 0:
        return f"{R}[DUE TODAY]{RESET}"
    if diff >= -3:
        return f"{Y}[due in {abs(diff)}d]{RESET}"
    return f"{DIM}[due {d.strftime('%b %d')}]{RESET}"


def section(title, char="="):
    width = 72
    print(f"\n{W}{char * width}{RESET}")
    print(f"{W}  {title}{RESET}")
    print(f"{W}{char * width}{RESET}")


def print_report(data):
    today = date.today()
    meta = data["metadata"]
    positions = data["positions"]
    candidates = data["candidates"]

    # ── Header ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print(f"{W}  DAILY PIPELINE STATUS REPORT  —  {today.strftime('%A, %B %d, %Y')}{RESET}")
    print(f"{DIM}  {meta['organization']}  |  Hiring Manager: {meta['hiring_manager']}{RESET}")
    print(f"{DIM}  Data last updated: {meta['last_updated']}{RESET}")
    print(f"{'=' * 72}")

    # ── Executive Summary ────────────────────────────────────────────────────
    section("EXECUTIVE SUMMARY", "-")
    active = [c for c in candidates if c["status"] in ACTIVE_STATUSES]
    hired  = [c for c in candidates if c["status"] == "HIRED"]
    primary = [c for c in candidates if c["status"] == "PRIMARY"]
    backups = [c for c in candidates if c["status"] == "BACKUP"]

    for pos_id, pos in positions.items():
        needed = pos["target_count"] - pos["hired_count"]
        colour = R if pos["status"] == "CRITICAL" else Y if pos["status"] == "URGENT" else G
        print(f"  {colour}[{pos['status']:8s}]{RESET}  {pos['title']}")
        print(f"           Target: {pos['target_count']}  |  Hired: {pos['hired_count']}  |  Still needed: {needed}")

    print()
    print(f"  Total active candidates  : {len(active)}")
    print(f"  {G}Hired{RESET}                    : {len(hired)}")
    print(f"  {C}Primary{RESET}                  : {len(primary)}")
    print(f"  {Y}Backup{RESET}                   : {len(backups)}")

    # ── Today's / Overdue Actions ────────────────────────────────────────────
    section("TODAY'S ACTIONS & OVERDUE ITEMS", "-")
    action_candidates = [
        c for c in candidates
        if c["next_action"] and c["status"] in ACTIVE_STATUSES
    ]
    action_candidates.sort(key=lambda c: parse_date(c.get("next_action_due")) or date(2099, 1, 1))

    overdue = [c for c in action_candidates if days_diff(parse_date(c.get("next_action_due"))) is not None and days_diff(parse_date(c.get("next_action_due"))) > 0]
    due_today = [c for c in action_candidates if days_diff(parse_date(c.get("next_action_due"))) == 0]
    upcoming = [c for c in action_candidates if days_diff(parse_date(c.get("next_action_due"))) is not None and -7 <= days_diff(parse_date(c.get("next_action_due"))) < 0]

    if overdue:
        print(f"\n  {R}OVERDUE:{RESET}")
        for c in overdue:
            tag = urgency_tag(c.get("next_action_due"))
            pos_title = positions[c["position"]]["title"]
            print(f"    {R}•{RESET} {W}{c['name']}{RESET} ({c['id']}) — {pos_title}")
            print(f"      {tag} {c['next_action']}")
            if c.get("phone"):
                print(f"      {DIM}Phone: {c['phone']}  Email: {c.get('email','—')}{RESET}")

    if due_today:
        print(f"\n  {Y}DUE TODAY:{RESET}")
        for c in due_today:
            tag = urgency_tag(c.get("next_action_due"))
            pos_title = positions[c["position"]]["title"]
            print(f"    {Y}•{RESET} {W}{c['name']}{RESET} ({c['id']}) — {pos_title}")
            print(f"      {tag} {c['next_action']}")
            if c.get("phone"):
                print(f"      {DIM}Phone: {c['phone']}  Email: {c.get('email','—')}{RESET}")

    if upcoming:
        print(f"\n  {C}UPCOMING (next 7 days):{RESET}")
        for c in upcoming:
            tag = urgency_tag(c.get("next_action_due"))
            pos_title = positions[c["position"]]["title"]
            print(f"    {C}•{RESET} {c['name']} ({c['id']}) — {pos_title}")
            print(f"      {tag} {c['next_action']}")

    if not overdue and not due_today and not upcoming:
        print(f"\n  {G}No urgent actions today.{RESET}")

    # ── Position-by-position breakdown ──────────────────────────────────────
    section("PIPELINE BY POSITION", "-")
    for pos_id, pos in positions.items():
        needed = pos["target_count"] - pos["hired_count"]
        colour = R if pos["status"] == "CRITICAL" else Y if pos["status"] == "URGENT" else G
        print(f"\n  {colour}[{pos_id}] {pos['title']}{RESET}")
        print(f"  {DIM}{'─' * 60}{RESET}")

        pos_candidates = [c for c in candidates if c["position"] == pos_id]
        for c in pos_candidates:
            sc = STATUS_COLOURS.get(c["status"], "")
            label = STATUS_LABELS.get(c["status"], c["status"])
            score_str = f"  Score: {c['score']}/10" if c["score"] else ""
            ctc_str = f"  Offer: ₹{c['offer_ctc']}" if c.get("offer_ctc") else ""
            joining_str = ""
            if c.get("joining_date"):
                jd = parse_date(c["joining_date"])
                delta = (jd - today).days
                joining_str = f"  Joining: {jd.strftime('%b %d, %Y')} ({delta}d away)"

            print(f"    {sc}[{label:12s}]{RESET}  {W}{c['name']}{RESET}{score_str}{ctc_str}{joining_str}")
            if c.get("next_action") and c["status"] in ACTIVE_STATUSES:
                tag = urgency_tag(c.get("next_action_due"))
                print(f"               Next: {c['next_action']} {tag}")

    # ── Upcoming Joiners ─────────────────────────────────────────────────────
    joiners = [c for c in candidates if c.get("joining_date") and c["status"] == "HIRED"]
    if joiners:
        section("UPCOMING JOINERS", "-")
        for c in joiners:
            jd = parse_date(c["joining_date"])
            delta = (jd - today).days
            colour = G if delta >= 0 else R
            print(f"  {colour}•{RESET} {c['name']} ({c['id']}) — {jd.strftime('%B %d, %Y')}  ({delta}d away)")
            print(f"    Position: {positions[c['position']]['title']}")

    # ── Risk Alerts ──────────────────────────────────────────────────────────
    section("RISK ALERTS", "-")
    risks = []

    for pos_id, pos in positions.items():
        primaries = [c for c in candidates if c["position"] == pos_id and c["status"] == "PRIMARY"]
        pos_backups = [c for c in candidates if c["position"] == pos_id and c["status"] == "BACKUP"]
        if pos["hired_count"] < pos["target_count"]:
            if not primaries:
                risks.append((R, f"[CRITICAL] {pos['title']}: NO primary candidate"))
            elif len(primaries) == 1 and not pos_backups:
                risks.append((Y, f"[RISK]     {pos['title']}: Only 1 primary, no backup"))

    backed_out = [c for c in candidates if c["status"] == "BACKED_OUT"]
    if backed_out:
        for c in backed_out:
            risks.append((R, f"[ALERT]    {c['name']} backed out of {positions[c['position']]['title']}"))

    if risks:
        for colour, msg in risks:
            print(f"  {colour}{msg}{RESET}")
    else:
        print(f"  {G}No critical risks identified.{RESET}")

    # ── Footer ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print(f"{DIM}  Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  Data: {DATA_FILE}{RESET}")
    print(f"{DIM}  To update candidate status: edit pipeline_data.json{RESET}")
    print(f"{'=' * 72}\n")


def save_report(data):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f"{date.today().isoformat()}.md")

    today = date.today()
    meta = data["metadata"]
    positions = data["positions"]
    candidates = data["candidates"]

    lines = [
        f"# Daily Pipeline Status — {today.strftime('%A, %B %d, %Y')}",
        f"**Organisation:** {meta['organization']}  |  **Hiring Manager:** {meta['hiring_manager']}",
        f"**Data last updated:** {meta['last_updated']}",
        "",
        "## Executive Summary",
        "",
    ]

    for pos_id, pos in positions.items():
        needed = pos["target_count"] - pos["hired_count"]
        lines.append(f"- **[{pos['status']}]** {pos['title']}: hired {pos['hired_count']}/{pos['target_count']} (need {needed})")

    lines += ["", "## Pipeline by Position", ""]
    for pos_id, pos in positions.items():
        lines.append(f"### {pos['title']} ({pos_id})")
        pos_candidates = [c for c in candidates if c["position"] == pos_id]
        for c in pos_candidates:
            label = STATUS_LABELS.get(c["status"], c["status"])
            score = f" | Score: {c['score']}/10" if c["score"] else ""
            ctc = f" | Offer: ₹{c['offer_ctc']}" if c.get("offer_ctc") else ""
            joining = f" | Joining: {c['joining_date']}" if c.get("joining_date") else ""
            lines.append(f"- **[{label}]** {c['name']} ({c['id']}){score}{ctc}{joining}")
            if c.get("next_action") and c["status"] in ACTIVE_STATUSES:
                due = f" _(due {c['next_action_due']})_" if c.get("next_action_due") else ""
                lines.append(f"  - Next: {c['next_action']}{due}")
        lines.append("")

    lines += [
        f"---",
        f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path


def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    data = load_data()
    print_report(data)

    if "--save" in sys.argv or "--report" in sys.argv:
        path = save_report(data)
        print(f"{DIM}  Markdown report saved: {path}{RESET}\n")

    candidates = data["candidates"]
    overdue = [
        c for c in candidates
        if c.get("next_action_due")
        and c["status"] in ACTIVE_STATUSES
        and days_diff(parse_date(c["next_action_due"])) > 0
    ]
    if overdue:
        sys.exit(2)


if __name__ == "__main__":
    main()
