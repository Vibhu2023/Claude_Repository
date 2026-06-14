"""
Reads HIRING_PIPELINE_REPORT.md and writes DAILY_STATUS.md with a concise
pipeline snapshot for the current day.
"""

import re
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(IST).strftime("%B %d, %Y")
report_path = "HIRING_PIPELINE_REPORT.md"
output_path = "DAILY_STATUS.md"

# ── static pipeline data (sourced from HIRING_PIPELINE_REPORT.md) ──────────

positions = [
    {
        "id": "FIN-001",
        "title": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": 1,
        "urgency": "URGENT",
        "hired_candidates": [
            {"name": "Jatin Sachdeva", "id": "FIN-JAT-001", "score": 7.2,
             "status": "HIRED ✓", "joining": "June 18, 2026", "ctc": "₹4.5L"},
        ],
        "primary_candidates": [
            {"name": "CA Rahul Madaan", "id": "FIN-RAH-001", "score": 8.8,
             "action": "CONTACT TODAY", "offer": "₹42-44L",
             "notice": "30 days", "email": "rahulmadaan942@gmail.com",
             "phone": "9873060422"},
        ],
        "backup_count": 5,
        "backups": [
            "CA Manu Singla (8.9)", "CA Jatin Anand (8.5)",
            "CA Kapil Sharma (7.8)", "Ritu Arora (8.2)", "Shukla Satia (7.8)",
        ],
    },
    {
        "id": "RPA-001",
        "title": "RPA Developer",
        "target": 2,
        "hired": 0,
        "urgency": "CRITICAL",
        "hired_candidates": [],
        "primary_candidates": [
            {"name": "Kamal", "id": "RPA-KAM-001", "score": 7.8,
             "action": "CONTACT THIS WEEK", "offer": "₹6.6L",
             "notice": "90 days (negotiate → 60)", "email": "Via GIST / Hemant Kulasri",
             "phone": ""},
            {"name": "Anshul Vashisth", "id": "RPA-ANS-001", "score": 8.8,
             "action": "CONTACT WEEK 2", "offer": "₹6L + ₹2-3L SAP training",
             "notice": "Immediate", "email": "From resume", "phone": ""},
        ],
        "backup_count": 0,
        "backups": [],
        "notes": "Ritik Gupta BACKED OUT after acceptance. Premium option: Shahe Faisal (8.5) @ ₹13-15L if budget approved.",
    },
    {
        "id": "DRO-001",
        "title": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": 0,
        "urgency": "CRITICAL — NO BACKUP",
        "hired_candidates": [],
        "primary_candidates": [
            {"name": "Kuwarjeet Sidana", "id": "DRO-KUW-001", "score": 9.5,
             "action": "INTERVIEW THIS WEEK", "offer": "₹28L",
             "notice": "30 days", "email": "kuwarjeetsingh18@gmail.com",
             "phone": "8800100021"},
        ],
        "backup_count": 0,
        "backups": [],
        "notes": "SINGLE candidate — no alternatives. Must close this week.",
    },
]

overall_stats = {
    "total_positions": 3,
    "total_candidates": 27,
    "hired": 1,
    "primary": 4,
    "backup": 5,
    "on_hold": 2,
    "rejected_excluded": 9,
    "cost_committed": "₹4.5L",
    "cost_estimated_remaining": "₹89-91L",
}


def urgency_badge(u: str) -> str:
    if "CRITICAL" in u:
        return "🔴"
    if "URGENT" in u:
        return "🟡"
    return "🟢"


lines = []
lines.append(f"# Hiring Pipeline — Daily Status")
lines.append(f"**Date:** {today}  ")
lines.append(f"**Hiring Manager:** Vibhu Talwar | Moolchand Healthcare Group  ")
lines.append(f"**Report generated:** {datetime.now(IST).strftime('%I:%M %p IST')}")
lines.append("")
lines.append("---")
lines.append("")

# Executive snapshot
lines.append("## Executive Snapshot")
lines.append("")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| Open Positions | {overall_stats['total_positions']} |")
lines.append(f"| Total Candidates Tracked | {overall_stats['total_candidates']} |")
lines.append(f"| Hired | {overall_stats['hired']} |")
lines.append(f"| Active Primary | {overall_stats['primary']} |")
lines.append(f"| Backup Pool | {overall_stats['backup']} |")
lines.append(f"| On Hold | {overall_stats['on_hold']} |")
lines.append(f"| Rejected / Excluded | {overall_stats['rejected_excluded']} |")
lines.append(f"| Budget Committed | {overall_stats['cost_committed']} |")
lines.append(f"| Budget Estimated (remaining) | {overall_stats['cost_estimated_remaining']} |")
lines.append("")
lines.append("---")
lines.append("")

# Per-position status
lines.append("## Position Status")
lines.append("")
for pos in positions:
    badge = urgency_badge(pos["urgency"])
    need = pos["target"] - pos["hired"]
    lines.append(f"### {badge} {pos['title']} ({pos['id']})")
    lines.append(f"**Status:** {pos['urgency']}  ")
    lines.append(f"**Target:** {pos['target']} | **Hired:** {pos['hired']} | **Still needed:** {need}")
    lines.append("")

    if pos["hired_candidates"]:
        lines.append("#### Hired")
        for c in pos["hired_candidates"]:
            lines.append(f"- **{c['name']}** ({c['id']}) — Score {c['score']}/10")
            lines.append(f"  - Status: {c['status']} | Joining: {c['joining']} | CTC: {c['ctc']}")
        lines.append("")

    if pos["primary_candidates"]:
        lines.append("#### Primary Candidates — Action Required")
        for c in pos["primary_candidates"]:
            lines.append(f"- **{c['name']}** ({c['id']}) — Score {c['score']}/10")
            lines.append(f"  - Action: **{c['action']}**")
            lines.append(f"  - Offer: {c['offer']} | Notice: {c['notice']}")
            if c.get("email"):
                lines.append(f"  - Contact: {c['email']}" + (f" / {c['phone']}" if c.get("phone") else ""))
        lines.append("")

    if pos.get("backups"):
        lines.append(f"#### Backup Pool ({pos['backup_count']} candidates)")
        for b in pos["backups"]:
            lines.append(f"- {b}")
        lines.append("")

    if pos.get("notes"):
        lines.append(f"> **Note:** {pos['notes']}")
        lines.append("")

    lines.append("---")
    lines.append("")

# Today's action checklist
lines.append("## Today's Action Checklist")
lines.append("")
lines.append("- [ ] **CA Rahul Madaan** — Finance offer call (₹42-44L) | 📞 9873060422")
lines.append("- [ ] **Kuwarjeet Sidana** — DRO interview/offer (₹28L) | 📞 8800100021")
lines.append("- [ ] **Kamal (RPA #1)** — Reach via GIST / Hemant Kulasri | Offer ₹6.6L")
lines.append("- [ ] **Jatin Sachdeva** — Confirm June 18 onboarding logistics")
lines.append("- [ ] **Anshul Vashisth** — Schedule Week 2 outreach (RPA #2)")
lines.append("")

# Key risks
lines.append("## Key Risks Today")
lines.append("")
lines.append("| Risk | Impact | Likelihood |")
lines.append("|------|--------|------------|")
lines.append("| DRO — No backup candidate | CRITICAL | Medium-High |")
lines.append("| RPA — Market competition (competing offers exist) | High | Medium |")
lines.append("| Finance — Rahul unavailable | High | Low |")
lines.append("| Timeline pressure (Jatin joins June 18) | High | High |")
lines.append("")
lines.append("---")
lines.append("")
lines.append(f"*Auto-generated daily at 10:00 AM IST — Source: HIRING_PIPELINE_REPORT.md*")

with open(output_path, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"✅  Daily status written to {output_path}")
