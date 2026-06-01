#!/usr/bin/env python3
"""Daily 10 AM candidate pipeline status updater for Moolchand Healthcare Group."""

from datetime import date, timedelta


CANDIDATES = {
    "FIN-JAT-001": {
        "name": "Jatin Sachdeva",
        "role": "Sr Finance Manager",
        "status": "HIRED",
        "score": 7.2,
        "ctc": "₹4.5L",
        "joining": date(2026, 6, 18),
        "contact": None,
    },
    "FIN-RAH-001": {
        "name": "CA Rahul Madaan",
        "role": "Sr Finance Manager",
        "status": "PRIMARY",
        "score": 8.8,
        "ctc": "₹42-44L",
        "joining": None,
        "contact": "9873060422 / rahulmadaan942@gmail.com",
    },
    "RPA-KAM-001": {
        "name": "Kamal",
        "role": "RPA Developer #1",
        "status": "PRIMARY",
        "score": 7.8,
        "ctc": "₹6.6L",
        "joining": None,
        "contact": "Via GIST - Hemant Kulasri",
    },
    "RPA-ANS-001": {
        "name": "Anshul Vashisth",
        "role": "RPA Developer #2",
        "status": "PRIMARY",
        "score": 8.8,
        "ctc": "₹6L + ₹2-3L training",
        "joining": None,
        "contact": "From resume",
    },
    "DRO-KUW-001": {
        "name": "Kuwarjeet Sidana",
        "role": "Chief Digital Revenue Officer",
        "status": "PRIMARY",
        "score": 9.5,
        "ctc": "₹28L",
        "joining": None,
        "contact": "8800100021 / kuwarjeetsingh18@gmail.com",
    },
}

MILESTONES = [
    (date(2026, 5, 20), "Contact Rahul Madaan (Finance)", "done"),
    (date(2026, 5, 20), "Contact Kuwarjeet Sidana (DRO)", "done"),
    (date(2026, 5, 21), "Outreach Kamal via GIST (RPA #1)", "done"),
    (date(2026, 5, 28), "Contact Anshul Vashisth (RPA #2)", "done"),
    (date(2026, 6, 1),  "Follow up all 4 primary candidates", "pending"),
    (date(2026, 6, 10), "Jatin Sachdeva onboarding prep", "upcoming"),
    (date(2026, 6, 18), "Jatin Sachdeva joins — Finance", "upcoming"),
    (date(2026, 6, 30), "Kuwarjeet Sidana target start — DRO", "upcoming"),
    (date(2026, 7, 31), "Kamal + Anshul expected start — RPA", "upcoming"),
]


def days_label(delta: int) -> str:
    if delta == 0:
        return "TODAY"
    if delta == 1:
        return "tomorrow"
    if delta < 0:
        return f"{abs(delta)} days ago"
    return f"in {delta} days"


def generate_report(today: date = None) -> str:
    today = today or date.today()
    lines = []

    lines.append("=" * 60)
    lines.append(f"  MOOLCHAND HEALTHCARE — DAILY PIPELINE UPDATE")
    lines.append(f"  {today.strftime('%B %d, %Y')} | 10:00 AM")
    lines.append("=" * 60)

    # Today's priority actions
    lines.append("\n>>> PRIORITY ACTIONS FOR TODAY <<<\n")
    hired = [c for c in CANDIDATES.values() if c["status"] == "HIRED"]
    primaries = [c for c in CANDIDATES.values() if c["status"] == "PRIMARY"]

    for c in primaries:
        lines.append(f"  [ ] Follow up: {c['name']} — {c['role']}")
        lines.append(f"      Contact: {c['contact']}")
        lines.append(f"      Offer:   {c['ctc']}")
        lines.append("")

    # Upcoming joining
    lines.append("\n>>> CONFIRMED HIRES — JOINING COUNTDOWN <<<\n")
    for c in hired:
        if c["joining"]:
            delta = (c["joining"] - today).days
            lines.append(
                f"  {c['name']} ({c['role']}) — joining {c['joining'].strftime('%B %d')} "
                f"[{days_label(delta)}]"
            )

    # Milestone tracker
    lines.append("\n>>> MILESTONE TRACKER <<<\n")
    for m_date, label, state in MILESTONES:
        delta = (m_date - today).days
        if state == "done":
            marker = "[DONE]"
        elif delta <= 0:
            marker = "[DUE]"
        elif delta <= 7:
            marker = "[THIS WEEK]"
        else:
            marker = "[UPCOMING]"
        lines.append(f"  {marker:12s} {m_date.strftime('%b %d')}  {label}")

    # Quick stats
    lines.append("\n>>> PIPELINE SNAPSHOT <<<\n")
    total = len(CANDIDATES)
    n_hired = sum(1 for c in CANDIDATES.values() if c["status"] == "HIRED")
    n_primary = sum(1 for c in CANDIDATES.values() if c["status"] == "PRIMARY")
    lines.append(f"  Total tracked:   {total}")
    lines.append(f"  Hired/Confirmed: {n_hired}")
    lines.append(f"  Awaiting offer:  {n_primary}")
    lines.append(f"  Open positions:  {3 - n_hired}")
    lines.append(f"  Est. cost (remaining): ₹89-91L")

    lines.append("\n" + "=" * 60)
    lines.append(f"  Next update: {(today + timedelta(days=1)).strftime('%B %d, %Y')} at 10:00 AM")
    lines.append("=" * 60)

    return "\n".join(lines)


def main() -> None:
    print(generate_report())


if __name__ == "__main__":
    main()
