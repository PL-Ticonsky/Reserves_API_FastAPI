"""
app/api/routers/me_appointments.py

Purpose:
- Client endpoints to manage their own appointments.
- Create, view, reschedule, and cancel appointments.

Notes:
- We keep 2 routers in the same file:
  1) /appointments (create)  -> global route
  2) /me/appointments (...)  -> client-owned routes
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_client
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreateIn,
    AppointmentOut,
)
from app.services.appointment_service import (
    create_client_appointment,
    AppointmentOverlapError,
    OutsideAvailabilityError,
    InvalidTimeRangeError,
)
from app.repositories.appointment_repo import (
    list_appointments_for_client,
    get_appointment_by_id,
)

from app.schemas.appointment import AppointmentOut
from app.services.appointment_service import cancel_client_appointment, AppointmentNotFoundError, InvalidStatusTransitionError

# Router for global /appointments endpoints
router = APIRouter(tags=["appointments"])

# Router for /me/appointments endpoints
me_router = APIRouter(prefix="/me", tags=["me-appointments"])


@router.post(
    "/appointments",
    response_model=AppointmentOut,
    status_code=status.HTTP_200_OK,
)
def create_appointment(
    payload: AppointmentCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
):
    """
    Create an appointment request for the authenticated client.
    Initial status: pending.
    """
    try:
        appt = create_client_appointment(
            db=db,
            client_id=current_user.id,
            start_at=payload.start_at,
            end_at=payload.end_at,
            description=payload.description,
        )
        return AppointmentOut.model_validate(appt)

    except AppointmentOverlapError:
        raise HTTPException(status_code=409, detail="APPOINTMENT_OVERLAP")
    except OutsideAvailabilityError:
        raise HTTPException(status_code=422, detail="OUTSIDE_AVAILABILITY")
    except InvalidTimeRangeError as e:
        raise HTTPException(status_code=422, detail=str(e))


@me_router.get(
    "/appointments",
    response_model=list[AppointmentOut],
    status_code=status.HTTP_200_OK,
)
def my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
):
    """
    GET /me/appointments
    List all appointments for the authenticated client.
    """
    appts = list_appointments_for_client(db, client_id=current_user.id)
    return [AppointmentOut.model_validate(a) for a in appts]


@me_router.get(
    "/appointments/{id}",
    response_model=AppointmentOut,
    status_code=status.HTTP_200_OK,
)
def my_appointment_by_id(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
):
    """
    GET /me/appointments/{id}
    Fetch one appointment if it belongs to the authenticated client.
    """
    appt = get_appointment_by_id(db, appointment_id=id)
    if appt is None:
        raise HTTPException(status_code=404, detail="APPOINTMENT_NOT_FOUND")
    if appt.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    return AppointmentOut.model_validate(appt)


@router.patch(
    "/me/appointments/{appointment_id}/cancel",
    response_model=AppointmentOut,
    status_code=status.HTTP_200_OK,
)
def cancel_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
):
    try:
        appt = cancel_client_appointment(db=db, client_id=current_user.id, appointment_id=appointment_id)
        return appt
    except AppointmentNotFoundError:
        raise HTTPException(status_code=404, detail="APPOINTMENT_NOT_FOUND")
    except InvalidStatusTransitionError:
        raise HTTPException(status_code=400, detail="INVALID_STATUS_TRANSITION")
