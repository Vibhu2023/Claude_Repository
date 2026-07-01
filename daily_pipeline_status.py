#!/usr/bin/env python3
"""Daily 10 AM hiring pipeline status check for Moolchand Healthcare Group.

Reads the candidate roster below and prints a status digest, flagging any
candidate whose expected joining/decision date has passed without the
report being marked resolved. Meant to be run each morning as part of the
"Hiring Pipeline Daily Status" calendar reminder.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Candidate:
    position: str
    name: str
    status: str
    expected_date: date | None
    contact: str


ROSTER = [
    Candidate("FIN-001 Sr Finance Manager", "Jatin Sachdeva", "HIRED - confirm onboarding", date(2026, 6, 18), "n/a"),
    Candidate("FIN-001 Sr Finance Manager", "CA Rahul Madaan", "PRIMARY - confirm offer acceptance", None, "rahulmadaan942@gmail.com | 9873060422"),
    Candidate("RPA-001 RPA Developer #1", "Kamal", "PRIMARY - via GIST/Hemant Kulasri", None, "GIST Consulting"),
    Candidate("RPA-001 RPA Developer #2", "Anshul Vashisth", "PRIMARY - confirm SAP training budget", None, "from resume"),
    Candidate("DRO-001 Chief Digital Revenue Officer", "Kuwarjeet Sidana", "PRIMARY - no backup, must close", date(2026, 6, 30), "kuwarjeetsingh18@gmail.com | 8800100021"),
]


def overdue(candidates: list[Candidate], today: date) -> list[Candidate]:
    return [c for c in candidates if c.expected_date and c.expected_date < today and "HIRED" not in c.status]


def print_status(today: date = date.today()) -> None:
    print(f"=== Hiring Pipeline Daily Status — {today.isoformat()} ===\n")
    for c in ROSTER:
        due = f" (expected {c.expected_date})" if c.expected_date else ""
        print(f"[{c.position}] {c.name}{due}")
        print(f"    Status: {c.status}")
        print(f"    Contact: {c.contact}\n")

    late = overdue(ROSTER, today)
    if late:
        print("!!! OVERDUE - needs manual confirmation:")
        for c in late:
            print(f"  - {c.name}: expected {c.expected_date}, still shows '{c.status}'")
    else:
        print("No overdue items.")


if __name__ == "__main__":
    print_status()
