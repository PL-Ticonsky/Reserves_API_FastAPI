"""
app/repositories/availability_repo.py

Purpose:
- Data access for provider availability blocks.
- Keep raw DB operations out of services/routers.

Notes:
- Services decide business rules (replace vs append, overlap checks, etc).
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.availability import Availability


def list_availability(db: Session) -> list[Availability]:
    stmt = select(Availability).order_by(Availability.weekday, Availability.start_time)
    return list(db.execute(stmt).scalars().all())


def delete_all_availability(db: Session) -> None:
    """
    Delete all availability blocks (used by REPLACE strategy).
    """
    db.execute(delete(Availability))


def bulk_create_availability(db: Session, blocks: list[Availability]) -> list[Availability]:
    """
    Insert many Availability rows.
    Returns the same list (after flush, ids should be present).
    """
    db.add_all(blocks)
    db.flush()
    return blocks
