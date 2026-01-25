"""
app/api/routers/barber_availability.py

Purpose:
- Provider endpoints to manage weekly availability.

Routes:
- POST /barber/availability/bulk (REPLACE strategy)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_provider
from app.db.session import get_db
from app.schemas.availability import AvailabilityBlockIn, AvailabilityBlockOut
from app.services.availability_service import replace_availability, AvailabilityOverlapError

router = APIRouter(prefix="/barber/availability", tags=["barber-availability"])


@router.post("/bulk", response_model=list[AvailabilityBlockOut], status_code=status.HTTP_201_CREATED)
def bulk_replace_availability(
    payload: list[AvailabilityBlockIn],
    db: Session = Depends(get_db),
    _provider=Depends(require_provider),
):
    """
    Replace the provider's weekly availability in bulk.

    Strategy:
    - Deletes all existing availability rows
    - Inserts the provided ones
    """
    try:
        rows = replace_availability(db, blocks_in=[p.model_dump() for p in payload])
        return [
            AvailabilityBlockOut(
                id=str(r.id),
                weekday=r.weekday,
                start_time=r.start_time,
                end_time=r.end_time,
                is_active=r.is_active,
            )
            for r in rows
        ]
    except AvailabilityOverlapError as e:
        raise HTTPException(status_code=422, detail=str(e))
