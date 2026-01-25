"""
app/services/appointment_service.py

Purpose:
- Business logic for client appointments.

Key rules enforced here:
1) start_at < end_at
2) Appointment must be within provider availability (weekly schedule)
3) Appointments cannot overlap (pending + confirmed block time)
4) Client can only create for themselves (client_id comes from token)

Important timezone rule:
- Availability is stored as (weekday, start_time, end_time) in LOCAL provider time.
- Appointments are stored as TIMESTAMPTZ (UTC).
- Therefore we validate using LOCAL time, then persist as given (TIMESTAMPTZ).
"""

from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment
from app.repositories.appointment_repo import create_appointment, find_overlapping_appointments
from app.repositories.availability_repo import list_availability
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.appointment_repo import get_appointment_by_id_for_client, set_appointment_status
from app.models.appointment import AppointmentStatus

class AppointmentNotFoundError(Exception): ...
class InvalidStatusTransitionError(Exception): ...
from zoneinfo import ZoneInfo
class OutsideAvailabilityError(ValueError):
    pass


class AppointmentOverlapError(ValueError):
    pass


class InvalidTimeRangeError(ValueError):
    pass

from app.repositories.appointment_repo import (
    list_appointments,
    get_appointment_by_id,
    set_appointment_status,
)


def _is_within_any_block(
    *,
    weekday: int,
    start_t: time,
    end_t: time,
    availability_blocks,
) -> bool:
    """
    Returns True if [start_t, end_t) is fully contained within at least one availability block.
    """
    for b in availability_blocks:
        if not b.is_active:
            continue
        if b.weekday != weekday:
            continue
        # contained: block.start <= start AND end <= block.end
        if b.start_time <= start_t and end_t <= b.end_time:
            return True
    return False


def create_client_appointment(
    db: Session,
    *,
    client_id: UUID,
    start_at: datetime,
    end_at: datetime,
    description: str | None = None,
) -> Appointment:
    """
    Create an appointment request for a client.

    Raises:
    - InvalidTimeRangeError
    - OutsideAvailabilityError
    - AppointmentOverlapError
    """
    if not (start_at < end_at):
        raise InvalidTimeRangeError("INVALID_TIME_RANGE")

    # ---- 1) Validate against provider availability (LOCAL time) ----
    tz_name = getattr(settings, "provider_timezone", "America/Bogota")
    provider_tz = ZoneInfo(tz_name)

    # Ensure timezone-aware
    if start_at.tzinfo is None or end_at.tzinfo is None:
        # For MVP: require timezone-aware inputs
        raise InvalidTimeRangeError("DATETIME_MUST_HAVE_TIMEZONE")

    start_local = start_at.astimezone(provider_tz)
    end_local = end_at.astimezone(provider_tz)

    # MVP decision: appointments must stay in the same local day
    if start_local.date() != end_local.date():
        raise InvalidTimeRangeError("CANNOT_CROSS_LOCAL_DAY")

    weekday = start_local.weekday()  # Monday=0..Sunday=6
    start_t = start_local.time()
    end_t = end_local.time()

    blocks = list_availability(db)

    if not _is_within_any_block(
        weekday=weekday,
        start_t=start_t,
        end_t=end_t,
        availability_blocks=blocks,
    ):
        raise OutsideAvailabilityError("OUTSIDE_AVAILABILITY")

    # ---- 2) Validate no overlap (DB times are TIMESTAMPTZ) ----
    overlaps = find_overlapping_appointments(db, start_at=start_at, end_at=end_at)
    if overlaps:
        raise AppointmentOverlapError("APPOINTMENT_OVERLAP")

    # ---- 3) Create appointment (pending by default) ----
    appt = create_appointment(
        db,
        client_id=client_id,
        start_at=start_at,
        end_at=end_at,
        description=description,
    )

    db.commit()
    db.refresh(appt)
    return appt


def cancel_client_appointment(db: Session, client_id: UUID, appointment_id: UUID):
    appt = get_appointment_by_id_for_client(db, appointment_id=appointment_id, client_id=client_id)
    if appt is None:
        raise AppointmentNotFoundError()

    if appt.status == AppointmentStatus.canceled:
        raise InvalidStatusTransitionError()

    appt = set_appointment_status(db, appt, AppointmentStatus.canceled)
    return appt




def list_barber_appointments(
    db: Session,
    *,
    dt_from: datetime | None,
    dt_to: datetime | None,
    status: str | None,
):
    status_enum = None
    if status is not None:
        # valida el string -> enum
        try:
            status_enum = AppointmentStatus(status)
        except ValueError:
            # status inválido: lo manejamos arriba con 422 normalmente
            raise ValueError("INVALID_STATUS_FILTER")

    return list_appointments(db, dt_from=dt_from, dt_to=dt_to, status=status_enum)

def confirm_appointment_as_provider(db: Session, *, appointment_id: UUID):
    appt = get_appointment_by_id(db, appointment_id)
    if appt is None:
        raise AppointmentNotFoundError()

    if appt.status != AppointmentStatus.pending:
        raise InvalidStatusTransitionError()

    return set_appointment_status(db, appt, new_status=AppointmentStatus.confirmed)

def cancel_appointment_as_provider(
    db: Session,
    *,
    appointment_id: UUID,
    reason: str | None,
):
    appt = get_appointment_by_id(db, appointment_id)
    if appt is None:
        raise AppointmentNotFoundError()

    if appt.status == AppointmentStatus.canceled:
        raise InvalidStatusTransitionError()

    # permite cancelar pending o confirmed
    return set_appointment_status(
        db,
        appt,
        new_status=AppointmentStatus.canceled,
        cancel_reason=reason,
    )

def reschedule_client_appointment(
    db: Session,
    *,
    client_id: UUID,
    appointment_id: UUID,
    start_at: datetime,
    end_at: datetime,
) -> Appointment:
    # 1) Validación básica
    if not (start_at < end_at):
        raise InvalidTimeRangeError("INVALID_TIME_RANGE")

    if start_at.tzinfo is None or end_at.tzinfo is None:
        raise InvalidTimeRangeError("DATETIME_MUST_HAVE_TIMEZONE")

    # 2) Buscar cita del cliente
    appt = get_appointment_by_id_for_client(db, appointment_id=appointment_id, client_id=client_id)
    if appt is None:
        raise AppointmentNotFoundError()

    # 3) MVP: solo reschedule si está pending
    if appt.status != AppointmentStatus.pending:
        raise InvalidStatusTransitionError()

    # 4) Validar availability (misma lógica que create)
    tz_name = getattr(settings, "provider_timezone", "America/Bogota")
    provider_tz = ZoneInfo(tz_name)

    start_local = start_at.astimezone(provider_tz)
    end_local = end_at.astimezone(provider_tz)

    if start_local.date() != end_local.date():
        raise InvalidTimeRangeError("CANNOT_CROSS_LOCAL_DAY")

    weekday = start_local.weekday()
    start_t = start_local.time()
    end_t = end_local.time()

    blocks = list_availability(db)
    if not _is_within_any_block(
        weekday=weekday,
        start_t=start_t,
        end_t=end_t,
        availability_blocks=blocks,
    ):
        raise OutsideAvailabilityError("OUTSIDE_AVAILABILITY")

    # 5) Validar overlap EXCLUYENDO esta cita
    overlaps = find_overlapping_appointments(
        db,
        start_at=start_at,
        end_at=end_at,
        exclude_appointment_id=appt.id,
    )
    if overlaps:
        raise AppointmentOverlapError("APPOINTMENT_OVERLAP")

    # 6) Actualizar horas (y mantener pending)
    from app.repositories.appointment_repo import update_appointment_time
    appt = update_appointment_time(db, appt, start_at=start_at, end_at=end_at)
    return appt
