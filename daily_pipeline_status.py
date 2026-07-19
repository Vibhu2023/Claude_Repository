#!/usr/bin/env python3
"""Daily hiring pipeline status check for Moolchand Healthcare Group."""

import sys
from datetime import date

LAST_VERIFIED = date(2026, 5, 19)
STALE_AFTER_DAYS = 7

POSITIONS = [
    {
        "id": "FIN-001",
        "name": "Sr Finance Manager / Finance & AR Lead",
        "candidates": [
            ("Jatin Sachdeva", "HIRED", "Joining June 18, 2026 - confirm onboarding"),
            ("CA Rahul Madaan", "PRIMARY", "Offer Rs.42-44L | 9873060422 | rahulmadaan942@gmail.com"),
        ],
    },
    {
        "id": "RPA-001",
        "name": "RPA Developer (2 positions)",
        "candidates": [
            ("Kamal", "PRIMARY #1", "Offer Rs.6.6L | via GIST Consulting - Hemant Kulasri"),
            ("Anshul Vashisth", "PRIMARY #2", "Offer Rs.6L + Rs.2-3L SAP training"),
            ("Shahe Faisal", "PREMIUM OPTIONAL", "Rs.13-15L if budget approved"),
        ],
    },
    {
        "id": "DRO-001",
        "name": "Chief Digital Revenue Officer",
        "candidates": [
            ("Kuwarjeet Sidana", "ONLY CANDIDATE - NO BACKUP", "Offer Rs.28L | 8800100021 | kuwarjeetsingh18@gmail.com"),
        ],
    },
]


def days_stale(today: date) -> int:
    return (today - LAST_VERIFIED).days


def main() -> None:
    today = date.today()
    stale_days = days_stale(today)

    print("=== Moolchand Healthcare Group - Hiring Pipeline Status ===")
    print(f"Checked: {today.isoformat()}")
    print(f"Data last verified: {LAST_VERIFIED.isoformat()} ({stale_days} days ago)")

    if stale_days > STALE_AFTER_DAYS:
        print(
            f"\nWARNING: Candidate status has not been manually verified in "
            f"{stale_days} days. Figures below reflect the last known state, "
            f"not confirmed current status. Contact candidates/GIST Consulting "
            f"directly to refresh before relying on this data."
        )

    for position in POSITIONS:
        print(f"\n{position['id']} | {position['name']}")
        for candidate_name, status, note in position["candidates"]:
            print(f"  - {candidate_name} ({status}) - {note}")

    print("\nFull detail: HIRING_PIPELINE_REPORT.md")


if __name__ == "__main__":
    sys.exit(main())
