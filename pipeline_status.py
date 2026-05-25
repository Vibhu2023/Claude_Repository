#!/usr/bin/env python3
"""Daily hiring pipeline status generator for Moolchand Healthcare Group."""

from datetime import date, timedelta
import sys


# ── Candidate data ────────────────────────────────────────────────────────────

POSITIONS = {
    "FIN-001": "Sr Finance Manager / Finance & AR Lead",
    "RPA-001": "RPA Developer",
    "DRO-001": "Chief Digital Revenue Officer",
}

CANDIDATES = [
    # Finance
    {
        "id": "FIN-JAT-001",
        "name": "Jatin Sachdeva",
        "position": "FIN-001",
        "score": 7.2,
        "status": "HIRED",
        "ctc": "₹4.5L",
        "notice_days": 0,
        "est_start": date(2026, 6, 18),
        "source": "GIST Consulting",
        "contact": "",
        "notes": "Joining confirmed June 18, 2026",
        "actions": [],
    },
    {
        "id": "FIN-RAH-001",
        "name": "CA Rahul Madaan",
        "position": "FIN-001",
        "score": 8.8,
        "status": "PRIMARY",
        "ctc": "₹42-44L",
        "notice_days": 30,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "rahulmadaan942@gmail.com | 9873060422",
        "notes": "Only viable Finance option. No red flags.",
        "actions": ["Contact today — offer ₹42-44L"],
    },
    {
        "id": "FIN-MAN-001",
        "name": "CA Manu Singla",
        "position": "FIN-001",
        "score": 8.9,
        "status": "BACKUP",
        "ctc": "TBD",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "Too junior (3 yrs). Activate if Rahul unavailable.",
        "actions": [],
    },
    {
        "id": "FIN-JAT-002",
        "name": "CA Jatin Anand",
        "position": "FIN-001",
        "score": 8.5,
        "status": "BACKUP",
        "ctc": "TBD",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "6 yrs experience. Backup #2.",
        "actions": [],
    },
    {
        "id": "FIN-KAP-001",
        "name": "CA Kapil Sharma",
        "position": "FIN-001",
        "score": 7.8,
        "status": "BACKUP",
        "ctc": "TBD",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "7 yrs experience. Backup #3.",
        "actions": [],
    },
    {
        "id": "FIN-RIT-001",
        "name": "Ritu Arora",
        "position": "FIN-001",
        "score": 8.2,
        "status": "BACKUP",
        "ctc": "₹31.67L",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "7 yrs, high CTC. Backup #4.",
        "actions": [],
    },
    {
        "id": "FIN-SHU-001",
        "name": "Shukla Satia",
        "position": "FIN-001",
        "score": 7.8,
        "status": "BACKUP",
        "ctc": "TBD",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "6 yrs experience. Backup #5.",
        "actions": [],
    },
    {
        "id": "FIN-ABH-001",
        "name": "CA Abhishek Goyal",
        "position": "FIN-001",
        "score": 9.3,
        "status": "DECLINED",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "Declined offer despite highest score.",
        "actions": [],
    },
    {
        "id": "FIN-VIK-001",
        "name": "Vikas Jain",
        "position": "FIN-001",
        "score": 7.5,
        "status": "REJECTED",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "Rejected by Moolchand — SAP gap, weak AR/C2C.",
        "actions": [],
    },
    # RPA
    {
        "id": "RPA-RIT-001",
        "name": "Ritik Gupta",
        "position": "RPA-001",
        "score": 8.8,
        "status": "BACKED OUT",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "GIST Consulting",
        "contact": "",
        "notes": "Was confirmed hired; withdrew after acceptance.",
        "actions": [],
    },
    {
        "id": "RPA-KAM-001",
        "name": "Kamal",
        "position": "RPA-001",
        "score": 7.8,
        "status": "PRIMARY",
        "ctc": "₹6.6L",
        "notice_days": 90,
        "est_start": date(2026, 7, 1),
        "source": "GIST Consulting",
        "contact": "Via GIST — Hemant Kulasri",
        "notes": "Negotiate notice 90→60 days. UiPath Orchestrator 5/5.",
        "actions": ["Contact this week via GIST — offer ₹6.6L"],
    },
    {
        "id": "RPA-ANS-001",
        "name": "Anshul Vashisth",
        "position": "RPA-001",
        "score": 8.8,
        "status": "PRIMARY",
        "ctc": "₹6L + ₹2-3L training",
        "notice_days": 0,
        "est_start": date(2026, 7, 1),
        "source": "Internal",
        "contact": "From resume",
        "notes": "SAP FICO integration — critical for HANA deployment.",
        "actions": ["Contact Week 2 — offer ₹6L + ₹2-3L SAP training"],
    },
    {
        "id": "RPA-SHA-001",
        "name": "Shahe Faisal",
        "position": "RPA-001",
        "score": 8.5,
        "status": "OPTIONAL",
        "ctc": "₹13-15L",
        "notice_days": 15,
        "est_start": None,
        "source": "PDF (May 18)",
        "contact": "",
        "notes": "Capgemini Rising Star. Competing: Cognizant ₹13L, TCS ₹13L. Premium tier only.",
        "actions": [],
    },
    {
        "id": "RPA-SUB-001",
        "name": "Subrat",
        "position": "RPA-001",
        "score": 0,
        "status": "EXCLUDED",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "",
        "contact": "",
        "notes": "Limited enterprise experience.",
        "actions": [],
    },
    {
        "id": "RPA-JAS-001",
        "name": "Jasmin Bar",
        "position": "RPA-001",
        "score": 0,
        "status": "EXCLUDED",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "",
        "contact": "",
        "notes": "Limited enterprise experience.",
        "actions": [],
    },
    {
        "id": "RPA-HAR-001",
        "name": "Hardik Agarwal",
        "position": "RPA-001",
        "score": 0,
        "status": "EXCLUDED",
        "ctc": "N/A",
        "notice_days": None,
        "est_start": None,
        "source": "",
        "contact": "",
        "notes": "Junior — mentorship-pair only.",
        "actions": [],
    },
    # DRO
    {
        "id": "DRO-KUW-001",
        "name": "Kuwarjeet Sidana",
        "position": "DRO-001",
        "score": 9.5,
        "status": "PRIMARY",
        "ctc": "₹28L",
        "notice_days": 30,
        "est_start": date(2026, 6, 20),
        "source": "GIST Consulting",
        "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
        "notes": "Only DRO candidate — NO BACKUP. Must close this week.",
        "actions": ["Interview this week — offer ₹28L. No backup available."],
    },
]

# ── Status ordering for display ───────────────────────────────────────────────

STATUS_ORDER = ["HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON HOLD",
                "BACKED OUT", "DECLINED", "REJECTED", "EXCLUDED", "WITHDRAWN"]

STATUS_BADGE = {
    "HIRED":       "✅ HIRED",
    "PRIMARY":     "🔵 PRIMARY",
    "BACKUP":      "🟡 BACKUP",
    "OPTIONAL":    "⚪ OPTIONAL",
    "ON HOLD":     "⏸  ON HOLD",
    "BACKED OUT":  "🔴 BACKED OUT",
    "DECLINED":    "🔴 DECLINED",
    "REJECTED":    "🔴 REJECTED",
    "EXCLUDED":    "⛔ EXCLUDED",
    "WITHDRAWN":   "🔴 WITHDRAWN",
}

ACTIVE_STATUSES = {"HIRED", "PRIMARY", "BACKUP", "OPTIONAL", "ON HOLD"}


# ── Report generation ─────────────────────────────────────────────────────────

def _header(today: date) -> str:
    return f"""# Moolchand Healthcare Group — Daily Hiring Pipeline Status
**Date:** {today.strftime("%B %d, %Y")}
**Hiring Manager:** Vibhu Talwar
**Auto-generated at:** 10:00 AM IST

---
"""


def _summary(today: date) -> str:
    status_counts: dict[str, int] = {}
    for c in CANDIDATES:
        status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1

    active = sum(status_counts.get(s, 0) for s in ACTIVE_STATUSES)
    hired = status_counts.get("HIRED", 0)
    primary = status_counts.get("PRIMARY", 0)

    lines = [
        "## Executive Summary\n",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Candidates | {len(CANDIDATES)} |",
        f"| Hired | {hired} |",
        f"| Primary (needs action) | {primary} |",
        f"| Active (all non-rejected) | {active} |",
    ]
    for s in STATUS_ORDER:
        if s not in ACTIVE_STATUSES and status_counts.get(s, 0) > 0:
            lines.append(f"| {s.title()} | {status_counts[s]} |")
    lines.append("")

    # Days-to-start countdown for hired/primary
    lines.append("### Joining Countdown\n")
    lines.append("| Candidate | Position | Est. Start | Days Remaining |")
    lines.append("|-----------|----------|------------|----------------|")
    for c in CANDIDATES:
        if c["status"] in ("HIRED", "PRIMARY") and c.get("est_start"):
            delta = (c["est_start"] - today).days
            flag = " ⚠️" if delta <= 7 else ""
            lines.append(
                f"| {c['name']} | {POSITIONS[c['position']]} "
                f"| {c['est_start'].strftime('%b %d, %Y')} "
                f"| {delta} days{flag} |"
            )
    lines.append("")
    return "\n".join(lines)


def _actions_dashboard(today: date) -> str:
    lines = ["## Today's Action Items\n"]
    any_action = False
    for c in CANDIDATES:
        if c["actions"]:
            any_action = True
            lines.append(f"- **{c['name']}** ({POSITIONS[c['position']]})  ")
            for a in c["actions"]:
                lines.append(f"  → {a}")
            if c["contact"]:
                lines.append(f"  📞 {c['contact']}")
    if not any_action:
        lines.append("_No open action items._")
    lines.append("")
    return "\n".join(lines)


def _position_section(pos_id: str) -> str:
    pos_candidates = [c for c in CANDIDATES if c["position"] == pos_id]
    pos_candidates.sort(key=lambda c: (STATUS_ORDER.index(c["status"]) if c["status"] in STATUS_ORDER else 99, -c["score"]))

    lines = [f"### {POSITIONS[pos_id]} ({pos_id})\n"]
    lines.append("| Candidate | Score | Status | CTC | Notice | Est. Start | Contact |")
    lines.append("|-----------|-------|--------|-----|--------|------------|---------|")
    for c in pos_candidates:
        badge = STATUS_BADGE.get(c["status"], c["status"])
        notice = f"{c['notice_days']}d" if c.get("notice_days") is not None else "—"
        start = c["est_start"].strftime("%b %d") if c.get("est_start") else "—"
        score = f"{c['score']}" if c["score"] else "—"
        contact = c["contact"] if c["contact"] else "—"
        lines.append(
            f"| {c['name']} | {score} | {badge} | {c['ctc']} | {notice} | {start} | {contact} |"
        )
    lines.append("")

    # Notes for active candidates
    for c in pos_candidates:
        if c["status"] in ACTIVE_STATUSES and c["notes"]:
            lines.append(f"**{c['name']}:** {c['notes']}  ")
    lines.append("")
    return "\n".join(lines)


def _risks() -> str:
    lines = [
        "## Key Risks\n",
        "| Risk | Impact | Mitigation |",
        "|------|--------|------------|",
        "| Rahul Madaan unavailable (Finance) | High | 5 backup candidates available |",
        "| DRO — Kuwarjeet: no backup | **CRITICAL** | Must close this week; have counter-offer ready |",
        "| RPA market competition | Medium-High | Fast-track contacts; Shahe Faisal as premium fallback |",
        "| Compressed timeline to June 18 | High | Parallel outreach; prep onboarding now |",
        "",
    ]
    return "\n".join(lines)


def generate_report(today: date | None = None, output_path: str | None = None) -> str:
    today = today or date.today()
    report = (
        _header(today)
        + _summary(today)
        + _actions_dashboard(today)
        + "## Pipeline by Position\n\n"
        + _position_section("FIN-001")
        + _position_section("RPA-001")
        + _position_section("DRO-001")
        + _risks()
        + f"\n---\n_Report auto-generated on {today.strftime('%B %d, %Y')} at 10:00 AM IST_\n"
    )
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report written to {output_path}")
    return report


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "DAILY_PIPELINE_STATUS.md"
    generate_report(output_path=path)
