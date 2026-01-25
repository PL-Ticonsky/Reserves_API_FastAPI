"""
app/services/availability_service.py

Purpose:
- Business logic for provider availability.
- Implements REPLACE strategy for bulk availability updates.

Rules:
- weekday in 0..6
- start_time < end_time
- no overlapping blocks within the same weekday (in the incoming payload)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import time

from sqlalchemy.orm import Session

from app.models.availability import Availability
from app.repositories.availability_repo import delete_all_availability, bulk_create_availability

from datetime import date as Date, datetime, timedelta, timezone
from app.repositories.availability_repo import list_availability

class AvailabilityOverlapError(ValueError):
    """Raised when incoming availability blocks overlap within the same weekday."""


def _overlaps(a_start: time, a_end: time, b_start: time, b_end: time) -> bool:
    """
    Returns True if [a_start, a_end) overlaps [b_start, b_end)
    """
    return a_start < b_end and b_start < a_end


def replace_availability(db: Session, *, blocks_in: list[dict]) -> list[Availability]:
    """
    Replace all existing availability with the provided blocks.

    Input format:
    - blocks_in: list of dicts with weekday, start_time, end_time

    Transaction behavior:
    - delete existing
    - insert new
    - commit
    """
    # 1) Validate no overlap inside payload per weekday
    by_day: dict[int, list[tuple[time, time]]] = defaultdict(list)

    for b in blocks_in:
        weekday = b["weekday"]
        start_time = b["start_time"]
        end_time = b["end_time"]
        by_day[weekday].append((start_time, end_time))

    for weekday, intervals in by_day.items():
        intervals_sorted = sorted(intervals, key=lambda x: x[0])
        for i in range(len(intervals_sorted) - 1):
            a_start, a_end = intervals_sorted[i]
            b_start, b_end = intervals_sorted[i + 1]
            if _overlaps(a_start, a_end, b_start, b_end):
                raise AvailabilityOverlapError(f"OVERLAP_IN_WEEKDAY_{weekday}")

    # 2) Build ORM objects
    rows = [
        Availability(
            weekday=b["weekday"],
            start_time=b["start_time"],
            end_time=b["end_time"],
            is_active=True,
        )
        for b in blocks_in
    ]

    # 3) Replace in DB
    delete_all_availability(db)
    bulk_create_availability(db, rows)

    db.commit()

    return rows



def generate_slots_for_date(
    db: Session,
    *,
    date: Date,
    slot_minutes: int = 30,
    tz_name: str = "America/Bogota",
) -> list[dict]:
    """
    Generate available slots for a given calendar date based on weekly availability.

    Returns:
        List[dict] like:
        [
          {"start_at": "2026-01-21T15:00:00Z", "end_at": "2026-01-21T15:30:00Z"},
          ...
        ]

    MVP Notes:
    - We generate slots only from availability blocks.
    - Later we will subtract existing appointments (pending/confirmed).
    - We return times in UTC (Z) to match the rest of the system.
    """
    if slot_minutes <= 0 or slot_minutes > 240:
        # keep it sane for MVP
        raise ValueError("INVALID_SLOT_MINUTES")

    weekday = date.weekday()  # Monday=0 ... Sunday=6

    # Pull availability blocks and filter for this weekday and active
    blocks = [
        b for b in list_availability(db)
        if b.is_active and b.weekday == weekday
    ]

    # If no blocks, just return empty list (200 [])
    slot_delta = timedelta(minutes=slot_minutes)

    # Use Python's built-in zoneinfo (no external dependency)
    from zoneinfo import ZoneInfo
    local_tz = ZoneInfo(tz_name)

    results: list[dict] = []

    for b in blocks:
        start_local = datetime.combine(date, b.start_time).replace(tzinfo=local_tz)
        end_local = datetime.combine(date, b.end_time).replace(tzinfo=local_tz)

        current = start_local
        while current + slot_delta <= end_local:
            slot_start_utc = current.astimezone(timezone.utc)
            slot_end_utc = (current + slot_delta).astimezone(timezone.utc)

            results.append(
                {
                    "start_at": slot_start_utc.isoformat().replace("+00:00", "Z"),
                    "end_at": slot_end_utc.isoformat().replace("+00:00", "Z"),
                }
            )

            current += slot_delta

    # Sort just in case
    results.sort(key=lambda x: x["start_at"])
    return results
