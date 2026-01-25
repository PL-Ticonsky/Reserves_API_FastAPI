from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_provider
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import AppointmentOut, AppointmentCancelIn

from app.services.appointment_service import (
    list_barber_appointments,
    confirm_appointment_as_provider,
    cancel_appointment_as_provider,
    AppointmentNotFoundError,
    InvalidStatusTransitionError,
)

router = APIRouter(prefix="/barber", tags=["barber"])

@router.get(
    "/appointments",
    response_model=list[AppointmentOut],
    status_code=status.HTTP_200_OK,
)
def get_all_appointments(
    db: Session = Depends(get_db),
    _provider: User = Depends(require_provider),
    from_: datetime | None = None,
    to: datetime | None = None,
    status_: str | None = None,
):
    """
    List barber appointments with optional filters.
    Query params:
      - from_ (datetime)  (nota: 'from' es keyword, por eso from_)
      - to (datetime)
      - status_ (pending|confirmed|canceled)
    """
    try:
        return list_barber_appointments(db, dt_from=from_, dt_to=to, status=status_)
    except ValueError as e:
        if str(e) == "INVALID_STATUS_FILTER":
            raise HTTPException(status_code=422, detail="INVALID_STATUS_FILTER")
        raise

@router.patch(
    "/appointments/{appointment_id}/confirm",
    response_model=AppointmentOut,
    status_code=status.HTTP_200_OK,
)
def confirm_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    _provider: User = Depends(require_provider),
):
    try:
        return confirm_appointment_as_provider(db, appointment_id=appointment_id)
    except AppointmentNotFoundError:
        raise HTTPException(status_code=404, detail="APPOINTMENT_NOT_FOUND")
    except InvalidStatusTransitionError:
        raise HTTPException(status_code=400, detail="INVALID_STATUS_TRANSITION")

@router.patch(
    "/appointments/{appointment_id}/cancel",
    response_model=AppointmentOut,
    status_code=status.HTTP_200_OK,
)
def cancel_appointment(
    appointment_id: UUID,
    payload: AppointmentCancelIn | None = None,
    db: Session = Depends(get_db),
    _provider: User = Depends(require_provider),
):
    reason = payload.reason if payload is not None else None
    try:
        return cancel_appointment_as_provider(db, appointment_id=appointment_id, reason=reason)
    except AppointmentNotFoundError:
        raise HTTPException(status_code=404, detail="APPOINTMENT_NOT_FOUND")
    except InvalidStatusTransitionError:
        raise HTTPException(status_code=400, detail="INVALID_STATUS_TRANSITION")
