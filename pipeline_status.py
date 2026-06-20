#!/usr/bin/env python3
"""Daily pipeline status report generator — Moolchand Healthcare Group."""

from datetime import date

TODAY = date.today()

# ── Candidate data ──────────────────────────────────────────────────────────

PIPELINE = {
    "FIN-001": {
        "role": "Sr Finance Manager / Finance & AR Lead",
        "target": 2,
        "hired": [
            {
                "id": "FIN-JAT-001",
                "name": "Jatin Sachdeva",
                "ctc": "₹4.5L",
                "score": 7.2,
                "joining_date": date(2026, 6, 18),
            }
        ],
        "primary": [
            {
                "id": "FIN-RAH-001",
                "name": "CA Rahul Madaan",
                "score": 8.8,
                "offer": "₹42-44L",
                "contact": "rahulmadaan942@gmail.com | 9873060422",
                "notice_days": 30,
                "est_start": date(2026, 6, 15),  # Mid-June
            }
        ],
        "backups": [
            "CA Manu Singla (8.9/10)",
            "CA Jatin Anand (8.5/10)",
            "CA Kapil Sharma (7.8/10)",
            "Ritu Arora (8.2/10)",
            "Shukla Satia (7.8/10)",
        ],
    },
    "RPA-001": {
        "role": "RPA Developer",
        "target": 2,
        "hired": [],
        "primary": [
            {
                "id": "RPA-KAM-001",
                "name": "Kamal",
                "score": 7.8,
                "offer": "₹6.6L",
                "contact": "Via GIST - Hemant Kulasri",
                "notice_days": 90,
                "est_start": date(2026, 7, 1),
            },
            {
                "id": "RPA-ANS-001",
                "name": "Anshul Vashisth",
                "score": 8.8,
                "offer": "₹6L + ₹2-3L SAP training",
                "contact": "Internal / Resume",
                "notice_days": 0,
                "est_start": date(2026, 7, 1),
            },
        ],
        "optional": {
            "name": "Shahe Faisal",
            "score": 8.5,
            "offer": "₹13-15L",
            "note": "Premium tier — needs budget approval",
        },
        "backed_out": "Ritik Gupta (was hired, withdrew post-acceptance)",
    },
    "DRO-001": {
        "role": "Chief Digital Revenue Officer",
        "target": 1,
        "hired": [],
        "primary": [
            {
                "id": "DRO-KUW-001",
                "name": "Kuwarjeet Sidana",
                "score": 9.5,
                "offer": "₹28L",
                "contact": "kuwarjeetsingh18@gmail.com | 8800100021",
                "notice_days": 30,
                "join_window_start": date(2026, 6, 15),
                "join_window_end": date(2026, 6, 30),
            }
        ],
        "backup": None,
    },
}


# ── Helpers ─────────────────────────────────────────────────────────────────

def _delta(d: date) -> str:
    diff = (d - TODAY).days
    if diff < 0:
        return f"{abs(diff)}d ago"
    if diff == 0:
        return "TODAY"
    return f"in {diff}d"


# ── Report ───────────────────────────────────────────────────────────────────

def generate_report() -> str:
    lines = []
    sep = "=" * 62

    lines += [
        sep,
        "  MOOLCHAND HEALTHCARE GROUP — DAILY PIPELINE STATUS",
        f"  {TODAY.strftime('%A, %B %d, %Y')}  |  Report Time: 10:00 AM IST",
        sep,
        "",
    ]

    alerts: list[str] = []
    total_hired = 0
    total_needed = sum(p["target"] for p in PIPELINE.values())

    for pos_id, pos in PIPELINE.items():
        role = pos["role"]
        target = pos["target"]
        hired_count = len(pos["hired"])
        total_hired += hired_count
        need = target - hired_count

        lines.append(f"[{pos_id}]  {role}")
        lines.append(f"  Target: {target}  |  Hired: {hired_count}  |  Still needed: {need}")

        # Hired
        for h in pos["hired"]:
            jd = h["joining_date"]
            if TODAY >= jd:
                join_note = f"JOINED {(TODAY - jd).days}d ago" if TODAY != jd else "JOINING TODAY"
            else:
                join_note = f"Joining {_delta(jd)} ({jd})"
            lines.append(f"  ✅ HIRED   {h['name']}  ({h['ctc']}, score {h['score']})  — {join_note}")

        # Primary
        for p in pos["primary"]:
            est = p.get("join_window_start") or p.get("est_start")
            est_note = f"Est. start: {est.strftime('%b %d')}" if est else ""

            # Window check for DRO
            win_start = p.get("join_window_start")
            win_end = p.get("join_window_end")
            if win_start and win_end:
                if TODAY < win_start:
                    status = f"Join window opens {_delta(win_start)}"
                elif TODAY <= win_end:
                    status = f"IN JOINING WINDOW ({win_start.strftime('%b %d')}–{win_end.strftime('%b %d')})"
                    alerts.append(
                        f"DRO: {p['name']} is in joining window "
                        f"({win_start.strftime('%b %d')}–{win_end.strftime('%b %d')}). Confirm join date!"
                    )
                else:
                    status = f"JOIN WINDOW PASSED ({win_end.strftime('%b %d')})"
                    alerts.append(
                        f"OVERDUE — DRO: {p['name']} joining window closed {_delta(win_end)}. "
                        "Immediate follow-up required!"
                    )
            elif est:
                days_to_start = (est - TODAY).days
                if days_to_start < 0:
                    status = f"Est. start was {abs(days_to_start)}d ago — check status"
                    alerts.append(
                        f"OVERDUE — {pos_id}: {p['name']} est. start was {abs(days_to_start)}d ago. "
                        "Confirm current status."
                    )
                elif days_to_start == 0:
                    status = "Est. start TODAY"
                    alerts.append(f"{pos_id}: {p['name']} expected to start TODAY.")
                else:
                    status = f"Est. start {_delta(est)} ({est.strftime('%b %d')})"
            else:
                status = "Status unknown"

            lines.append(
                f"  🔵 PRIMARY  {p['name']}  (score {p['score']})  — {p['offer']}"
            )
            lines.append(f"             Contact: {p['contact']}")
            lines.append(f"             {status}")

        # Backups
        if pos.get("backups"):
            lines.append(f"  📋 Backups: {', '.join(pos['backups'])}")

        # Optional / special notes
        if pos.get("optional"):
            opt = pos["optional"]
            lines.append(
                f"  ⚡ OPTIONAL {opt['name']} (score {opt['score']}) — {opt['offer']}  [{opt['note']}]"
            )
        if pos.get("backed_out"):
            lines.append(f"  ❌ BACKED OUT: {pos['backed_out']}")
        if pos.get("backup") is None and pos_id == "DRO-001":
            lines.append("  ⚠️  NO BACKUP CANDIDATE for DRO role")

        lines.append("")

    # ── Summary ──
    open_positions = total_needed - total_hired
    lines += [
        "─" * 62,
        "PIPELINE SUMMARY",
        "─" * 62,
        f"  Positions filled  : {total_hired} / {total_needed}",
        f"  Positions open    : {open_positions}",
        f"  Estimated cost    : ₹4.5L committed  +  ₹89-91L pending",
        "",
    ]

    # ── Alerts ──
    if alerts:
        lines.append(f"⚠️  ACTION REQUIRED TODAY ({TODAY.strftime('%b %d')}):")
        for i, a in enumerate(alerts, 1):
            lines.append(f"  {i}. {a}")
    else:
        lines.append("✅  No critical alerts today.")

    lines += [
        "",
        sep,
        "  Next automated update: Tomorrow 10:00 AM IST",
        sep,
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())
