"""
Daily hiring pipeline status report generator.
Run this script daily at 10 AM IST to produce DAILY_STATUS_UPDATE.md.

Usage: python generate_daily_status.py
"""

from datetime import date, datetime, timedelta
import os


CANDIDATES = {
    "finance": [
        {
            "id": "FIN-JAT-001",
            "name": "Jatin Sachdeva",
            "role": "Finance Manager / AR Lead",
            "status": "HIRED",
            "ctc": "₹4.5L",
            "joining": date(2026, 6, 18),
            "email": None,
            "phone": None,
            "score": 7.2,
            "note": "Confirmed hire — joining June 18, 2026",
        },
        {
            "id": "FIN-RAH-001",
            "name": "CA Rahul Madaan",
            "role": "Finance Manager / AR Lead",
            "status": "PRIMARY",
            "cTC_offer": "₹42–44L",
            "notice_days": 30,
            "email": "rahulmadaan942@gmail.com",
            "phone": "9873060422",
            "score": 8.8,
            "note": "Only viable Finance option — contact today",
        },
        {
            "id": "FIN-MAN-001",
            "name": "CA Manu Singla",
            "role": "Finance Manager / AR Lead",
            "status": "BACKUP",
            "score": 8.9,
            "note": "Too junior (3 yrs) — activate if Rahul declines",
        },
        {
            "id": "FIN-JAT-002",
            "name": "CA Jatin Anand",
            "role": "Finance Manager / AR Lead",
            "status": "BACKUP",
            "score": 8.5,
            "note": "6 years experience",
        },
        {
            "id": "FIN-KAP-001",
            "name": "CA Kapil Sharma",
            "role": "Finance Manager / AR Lead",
            "status": "BACKUP",
            "score": 7.8,
            "note": "7 years experience — tier 3 fallback",
        },
        {
            "id": "FIN-RIT-001",
            "name": "Ritu Arora",
            "role": "Finance Manager / AR Lead",
            "status": "BACKUP",
            "score": 8.2,
            "note": "High CTC ₹31.67L — tier 3 fallback",
        },
        {
            "id": "FIN-SHU-001",
            "name": "Shukla Satia",
            "role": "Finance Manager / AR Lead",
            "status": "BACKUP",
            "score": 7.8,
            "note": "6 years experience — tier 3 fallback",
        },
    ],
    "rpa": [
        {
            "id": "RPA-KAM-001",
            "name": "Kamal",
            "role": "RPA Developer",
            "status": "PRIMARY",
            "cTC_offer": "₹6.6L",
            "notice_days": 90,
            "contact_via": "GIST — Hemant Kulasri",
            "score": 7.8,
            "note": "UiPath Orchestrator expert — target July 2026 start",
        },
        {
            "id": "RPA-ANS-001",
            "name": "Anshul Vashisth",
            "role": "RPA Developer",
            "status": "PRIMARY",
            "cTC_offer": "₹6L + ₹2–3L SAP training",
            "notice_days": 0,
            "email": None,
            "score": 8.8,
            "note": "SAP FICO integration — critical for HANA. Target July 2026 start",
        },
        {
            "id": "RPA-SHA-001",
            "name": "Shahe Faisal",
            "role": "RPA Developer",
            "status": "OPTIONAL",
            "cTC_offer": "₹13–15L",
            "notice_days": 15,
            "score": 8.5,
            "note": "Premium tier — only if ₹15L budget approved",
        },
        {
            "id": "RPA-RIT-001",
            "name": "Ritik Gupta",
            "role": "RPA Developer",
            "status": "BACKED_OUT",
            "score": 8.8,
            "note": "Was hired; withdrew after acceptance",
        },
    ],
    "dro": [
        {
            "id": "DRO-KUW-001",
            "name": "Kuwarjeet Sidana",
            "role": "Chief Digital Revenue Officer",
            "status": "PRIMARY",
            "cTC_offer": "₹28L",
            "notice_days": 30,
            "joining_window": (date(2026, 6, 15), date(2026, 6, 30)),
            "email": "kuwarjeetsingh18@gmail.com",
            "phone": "8800100021",
            "score": 9.5,
            "note": "Only DRO candidate — no backup. Must close immediately",
        },
    ],
}

STATUS_EMOJI = {
    "HIRED": "✅",
    "PRIMARY": "🟠",
    "BACKUP": "🟡",
    "OPTIONAL": "🟡",
    "BACKED_OUT": "❌",
    "REJECTED": "❌",
    "ON_HOLD": "⏸️",
}


def build_alerts(today: date) -> list[str]:
    alerts = []

    for c in CANDIDATES["finance"]:
        if c["status"] == "HIRED" and c.get("joining") == today:
            alerts.append(
                f"🔴 CRITICAL | {c['name']} **JOINING TODAY** (Finance) | "
                "Confirm onboarding & first-day logistics"
            )

    dro = CANDIDATES["dro"][0]
    window = dro.get("joining_window")
    if window and window[0] <= today <= window[1]:
        alerts.append(
            f"🔴 CRITICAL | {dro['name']} (DRO) — confirm start date | "
            f"Est. window: {window[0].strftime('%b %d')}–{window[1].strftime('%b %d')}. Verify if joined"
        )

    finance_primary = next(
        (c for c in CANDIDATES["finance"] if c["status"] == "PRIMARY"), None
    )
    if finance_primary:
        alerts.append(
            f"🟠 HIGH | {finance_primary['name']} (Finance) — follow-up overdue | "
            "30 days since initial contact (May 19)"
        )

    rpa_primaries = [c for c in CANDIDATES["rpa"] if c["status"] == "PRIMARY"]
    if rpa_primaries:
        alerts.append(
            "🟠 HIGH | RPA positions still unfilled | "
            f"{' & '.join(c['name'] for c in rpa_primaries)} targeted for July"
        )

    return alerts


def render_report(today: date) -> str:
    ts = f"{today.strftime('%B %d, %Y')} | **Generated:** 10:00 AM IST"
    alerts = build_alerts(today)
    alert_rows = "\n".join(
        f"| {a.split(' | ')[0]} | {a.split(' | ')[1]} | {a.split(' | ')[2]} |"
        for a in alerts
    )

    tomorrow = today + timedelta(days=1)

    report = f"""# Moolchand Healthcare Group — Daily Hiring Pipeline Status
**Date:** {ts}
**Hiring Manager:** Vibhu Talwar

---

## TODAY'S ALERTS

| Priority | Alert | Action |
|----------|-------|--------|
{alert_rows}

---

## Position-by-Position Status

### 1. Finance Manager / AR Lead (FIN-001)

| Candidate | Status | Score | Next Step |
|-----------|--------|-------|-----------|
"""

    for c in CANDIDATES["finance"]:
        emoji = STATUS_EMOJI.get(c["status"], "❓")
        step = c.get("note", "—")
        report += f"| {c['name']} | {emoji} {c['status']} | {c['score']}/10 | {step} |\n"

    report += """
---

### 2. RPA Developer (RPA-001) — Need 2 (CRITICAL — 0 hired)

| Candidate | Status | Score | CTC Offer | Next Step |
|-----------|--------|-------|-----------|-----------|
"""

    for c in CANDIDATES["rpa"]:
        emoji = STATUS_EMOJI.get(c["status"], "❓")
        cTC = c.get("cTC_offer", "—")
        step = c.get("note", "—")
        report += f"| {c['name']} | {emoji} {c['status']} | {c['score']}/10 | {cTC} | {step} |\n"

    report += """
---

### 3. Chief Digital Revenue Officer (DRO-001) — Need 1

| Candidate | Status | Score | CTC Offer | Next Step |
|-----------|--------|-------|-----------|-----------|
"""

    for c in CANDIDATES["dro"]:
        emoji = STATUS_EMOJI.get(c["status"], "❓")
        cTC = c.get("cTC_offer", "—")
        step = c.get("note", "—")
        report += f"| {c['name']} | {emoji} {c['status']} | {c['score']}/10 | {cTC} | {step} |\n"

    report += f"""
---

## Today's Action Checklist

- [ ] **Finance:** Welcome Jatin Sachdeva on Day 1 — confirm all onboarding docs
- [ ] **Finance:** Call Rahul Madaan — 9873060422 / rahulmadaan942@gmail.com — get offer decision
- [ ] **DRO:** Confirm Kuwarjeet Sidana's joining status — 8800100021 / kuwarjeetsingh18@gmail.com
- [ ] **RPA:** Get update from GIST (Hemant Kulasri) on Kamal's offer acceptance
- [ ] **RPA:** Confirm Anshul Vashisth's status and SAP training budget approval
- [ ] **Finance (contingency):** If Rahul declines → activate CA Manu Singla or CA Jatin Anand

---

*Next update: {tomorrow.strftime('%B %d, %Y')} at 10:00 AM IST*
*Report auto-generated for: Vibhu Talwar, Hiring Manager*
"""

    return report


def main():
    today = date.today()
    report = render_report(today)
    output_path = os.path.join(os.path.dirname(__file__), "DAILY_STATUS_UPDATE.md")
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Daily status report written to {output_path}")


if __name__ == "__main__":
    main()
