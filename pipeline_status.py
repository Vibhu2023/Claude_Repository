#!/usr/bin/env python3
"""Daily hiring pipeline status report generator.

Run directly for console output. GitHub Actions calls this at 10 AM IST
and commits the updated DAILY_STATUS.md to the repository.

Usage:
    python pipeline_status.py              # print to console
    python pipeline_status.py --save       # also write DAILY_STATUS.md
"""

import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "candidates.json"
OUTPUT_FILE = Path(__file__).parent / "DAILY_STATUS.md"

STATUS_LABEL = {
    "HIRED": "HIRED",
    "PRIMARY": "PRIMARY",
    "BACKUP": "BACKUP",
    "OPTIONAL": "OPTIONAL",
    "ON_HOLD": "ON HOLD",
    "EXCLUDED": "EXCLUDED",
    "REJECTED": "REJECTED",
    "WITHDRAWN": "WITHDRAWN",
    "BACKED_OUT": "BACKED OUT",
}

ACTIVE_STATUSES = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON_HOLD"}

URGENCY_BADGE = {"CRITICAL": "[CRITICAL]", "URGENT": "[URGENT]", "NORMAL": ""}


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def days_to_date(target_str: str | None) -> str:
    if not target_str:
        return ""
    try:
        target = date.fromisoformat(target_str)
        delta = (target - date.today()).days
        if delta < 0:
            return f"(joined {abs(delta)}d ago)"
        if delta == 0:
            return "(JOINING TODAY)"
        return f"(in {delta} days)"
    except ValueError:
        return ""


def build_report(data: dict) -> str:
    today = date.today()
    positions = {p["id"]: p for p in data["positions"]}
    candidates_by_position: dict[str, list] = defaultdict(list)
    for c in data["candidates"]:
        candidates_by_position[c["position_id"]].append(c)

    lines: list[str] = []

    lines.append(f"# Moolchand Healthcare Group — Hiring Pipeline Status")
    lines.append(f"**Date:** {today.strftime('%A, %B %d, %Y')}  ")
    lines.append(f"**Data last updated:** {data['last_updated']}  ")
    lines.append(f"**Hiring Manager:** {data['report_metadata']['hiring_manager']}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Summary table ---
    total_target = sum(p["target_headcount"] for p in data["positions"])
    total_hired = sum(p["hired"] for p in data["positions"])
    total_needed = total_target - total_hired
    all_primary = [c for c in data["candidates"] if c["status"] == "PRIMARY"]
    all_backup = [c for c in data["candidates"] if c["status"] == "BACKUP"]

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Open Positions | {total_target} |")
    lines.append(f"| Hired | {total_hired} / {total_target} |")
    lines.append(f"| Still Needed | **{total_needed}** |")
    lines.append(f"| Active Primary Candidates | {len(all_primary)} |")
    lines.append(f"| Backup Candidates | {len(all_backup)} |")
    lines.append(f"| Total Candidates Tracked | {len(data['candidates'])} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Per-position breakdown ---
    lines.append("## Position Status")
    lines.append("")

    for pos in data["positions"]:
        pid = pos["id"]
        still_need = pos["target_headcount"] - pos["hired"]
        badge = URGENCY_BADGE.get(pos["urgency"], "")
        fill_status = (
            "FILLED" if still_need == 0 else f"NEED {still_need} MORE {badge}"
        )
        lines.append(
            f"### {pos['title']} ({pid})"
        )
        lines.append(
            f"**Target:** {pos['target_headcount']} | "
            f"**Hired:** {pos['hired']} | "
            f"**Status:** {fill_status}"
        )
        lines.append("")

        cands = sorted(
            candidates_by_position[pid],
            key=lambda c: (
                list(STATUS_LABEL.keys()).index(c["status"])
                if c["status"] in STATUS_LABEL
                else 99
            ),
        )

        for c in cands:
            if c["status"] not in ACTIVE_STATUSES:
                continue
            label = STATUS_LABEL.get(c["status"], c["status"])
            score_str = f" | Score: {c['score']}/10" if c["score"] else ""
            ctc_str = f" | CTC: ₹{c['current_ctc']}" if c["current_ctc"] else ""
            offer_str = f" | Offer: ₹{c['offered_ctc']}" if c["offered_ctc"] else ""
            notice_str = (
                f" | Notice: {c['notice_days']}d" if c["notice_days"] is not None else ""
            )
            join_hint = days_to_date(c.get("joining_date"))
            join_str = (
                f" | Joining: {c['joining_date']} {join_hint}"
                if c.get("joining_date")
                else ""
            )
            contact_parts = []
            if c.get("email"):
                contact_parts.append(c["email"])
            if c.get("phone"):
                contact_parts.append(c["phone"])
            contact_str = (
                f" | Contact: {' / '.join(contact_parts)}" if contact_parts else ""
            )
            notes_str = f"  \n  > {c['notes']}" if c["notes"] else ""

            lines.append(
                f"- **[{label}]** {c['name']} ({c['id']})"
                f"{score_str}{ctc_str}{offer_str}{notice_str}{join_str}{contact_str}"
                f"{notes_str}"
            )

        inactive = [c for c in cands if c["status"] not in ACTIVE_STATUSES]
        if inactive:
            inactive_names = ", ".join(
                f"{c['name']} ({STATUS_LABEL.get(c['status'], c['status'])})"
                for c in inactive
            )
            lines.append(f"- *Inactive:* {inactive_names}")

        lines.append("")

    # --- Today's actions ---
    lines.append("---")
    lines.append("")
    lines.append("## Today's Actions")
    lines.append("")

    actions = _build_actions(data, today)
    if actions:
        for action in actions:
            lines.append(f"- {action}")
    else:
        lines.append("_No outstanding actions identified._")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Risks")
    lines.append("")
    lines.append(
        "| # | Risk | Impact | Mitigation |"
    )
    lines.append("|---|------|--------|------------|")
    lines.append(
        "| 1 | Finance - Rahul Madaan unavailable | High | 5 backup candidates available |"
    )
    lines.append(
        "| 2 | RPA - competitive market / counter-offers | High | Fast-track; Shahe Faisal as premium fallback |"
    )
    lines.append(
        "| 3 | DRO - Kuwarjeet Sidana, NO backup | CRITICAL | Must close this week; prepare counter-offer |"
    )
    lines.append(
        "| 4 | Compressed timeline (June–July joining) | High | Parallel outreach + onboarding prep now |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"_Report auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} IST_"
    )

    return "\n".join(lines)


def _build_actions(data: dict, today: date) -> list[str]:
    actions = []
    for c in data["candidates"]:
        if c["status"] == "PRIMARY":
            name = c["name"]
            pos_id = c["position_id"]
            contact_parts = []
            if c.get("email"):
                contact_parts.append(c["email"])
            if c.get("phone"):
                contact_parts.append(c["phone"])
            contact = " / ".join(contact_parts) if contact_parts else c.get("source", "via source")
            offer = f"₹{c['offered_ctc']}" if c.get("offered_ctc") else "per budget"
            actions.append(
                f"**{pos_id} — {name}:** Follow up / confirm offer {offer} | {contact}"
            )

    for c in data["candidates"]:
        if c["status"] == "HIRED" and c.get("joining_date"):
            join = date.fromisoformat(c["joining_date"])
            delta = (join - today).days
            if 0 <= delta <= 7:
                actions.append(
                    f"**Onboarding — {c['name']}:** Joining {c['joining_date']} "
                    f"({delta}d) — confirm logistics"
                )

    return actions


def main() -> None:
    save = "--save" in sys.argv
    data = load_data()
    report = build_report(data)

    print(report)

    if save:
        OUTPUT_FILE.write_text(report, encoding="utf-8")
        print(f"\n[Saved to {OUTPUT_FILE}]", file=sys.stderr)


if __name__ == "__main__":
    main()
