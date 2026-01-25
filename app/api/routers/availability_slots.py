"""
app/api/routers/availability_slots.py

Purpose:
- Client endpoint to view available booking slots for a given date.
- Slots are computed from weekly availability (and later: minus taken appointments).

Route:
- GET /availability/slots?date=YYYY-MM-DD&slot_minutes=30
"""

from __future__ import annotations

from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_client
from app.db.session import get_db
from app.core.config import settings
from app.services.availability_service import generate_slots_for_date

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("/slots", status_code=status.HTTP_200_OK)
def get_availability_slots(
    date: Date = Query(..., description="Calendar date in YYYY-MM-DD"),
    slot_minutes: int = Query(30, ge=5, le=240),
    db: Session = Depends(get_db),
    _client=Depends(require_client),
):
    """
    Returns computed availability slots for the requested date.

    Notes:
    - Requires client auth (per your contract).
    - Returns UTC datetimes (Z).
    """
    try:
        return generate_slots_for_date(
            db,
            date=date,
            slot_minutes=slot_minutes,
            tz_name=getattr(settings, "provider_timezone", "America/Bogota"),
        )
    except ValueError as e:
        # For now keep it simple; later we can use a standard error format
        raise HTTPException(status_code=422, detail=str(e))
