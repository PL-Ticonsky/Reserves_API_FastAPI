"""

Purpose:
- Data access layer for appointments.
- Contains raw SQLAlchemy queries (no business rules).

Responsibilities:
- Create appointments
- Query appointments by client/provider views
- Detect overlaps in a given time range

Important:
- Overlap logic is used by services to enforce "no overlap" rule.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus


def create_appointment(
    db: Session,
    *,
    client_id: UUID,
    start_at: datetime,
    end_at: datetime,
    description: str | None = None,
) -> Appointment:
    """
    Insert a new appointment as 'pending' by default (DB default).

    Returns:
        The created Appointment (after flush, id is available).
    """
    appt = Appointment(
        client_id=client_id,
        start_at=start_at,
        end_at=end_at,
        description=description,
        # status left to DB default = pending
    )
    db.add(appt)
    db.flush()  # ensures appt.id exists without committing
    return appt


def get_appointment_by_id(db: Session, *, appointment_id: UUID) -> Appointment | None:
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    return db.execute(stmt).scalars().first()


def list_appointments_for_client(
    db: Session,
    *,
    client_id: UUID,
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    status: AppointmentStatus | None = None,
) -> list[Appointment]:
    """
    List a client's appointments with optional filters.
    """
    stmt = select(Appointment).where(Appointment.client_id == client_id)

    if from_dt is not None:
        stmt = stmt.where(Appointment.start_at >= from_dt)
    if to_dt is not None:
        stmt = stmt.where(Appointment.end_at <= to_dt)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at.asc())
    return list(db.execute(stmt).scalars().all())


def find_overlapping_appointments(
    db: Session,
    *,
    start_at: datetime,
    end_at: datetime,
    exclude_appointment_id: UUID | None = None,
) -> list[Appointment]:
    """
    Find appointments that overlap the interval [start_at, end_at).

    Overlap condition:
        existing.start < requested.end AND requested.start < existing.end

    We consider blocking statuses only:
    - pending
    - confirmed
    (canceled does not block time)

    exclude_appointment_id:
    - used for reschedule, to ignore the appointment being moved
    """
    stmt = select(Appointment).where(
        and_(
            Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]),
            Appointment.start_at < end_at,
            start_at < Appointment.end_at,
        )
    )

    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)

    stmt = stmt.order_by(Appointment.start_at.asc())
    return list(db.execute(stmt).scalars().all())




def get_appointment_by_id_for_client(db: Session, appointment_id: UUID, client_id: UUID) -> Appointment | None:
    return (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.client_id == client_id)
        .one_or_none()
    )

def set_appointment_status(db: Session, appt: Appointment, status: AppointmentStatus) -> Appointment:
    appt.status = status
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt



def list_appointments(
    db: Session,
    *,
    dt_from: datetime | None = None,
    dt_to: datetime | None = None,
    status: AppointmentStatus | None = None,
) -> list[Appointment]:
    stmt = select(Appointment)

    if dt_from is not None:
        stmt = stmt.where(Appointment.start_at >= dt_from)
    if dt_to is not None:
        stmt = stmt.where(Appointment.end_at <= dt_to)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at.asc())
    return list(db.execute(stmt).scalars().all())

def get_appointment_by_id(db: Session, appointment_id: UUID) -> Appointment | None:
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    return db.execute(stmt).scalars().one_or_none()

def set_appointment_status(
    db: Session,
    appt: Appointment,
    *,
    new_status: AppointmentStatus,
    cancel_reason: str | None = None,
) -> Appointment:
    appt.status = new_status
    if cancel_reason is not None:
        appt.cancel_reason = cancel_reason

    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt
