"""
app/schemas/appointment.py

Purpose:
- Pydantic schemas for Appointment requests/responses.
- Used by client and provider appointment endpoints.

Design:
- Input datetimes are accepted in ISO 8601 (with timezone offset).
- Internally we will store datetimes as TIMESTAMPTZ (UTC in DB).
- Status is controlled by backend (client creates -> pending).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional



class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"


class AppointmentCreateIn(BaseModel):
    """
    Body for POST /appointments
    Client requests a new appointment.
    """
    start_at: datetime
    end_at: datetime
    description: str | None = Field(default=None, max_length=500)

    @field_validator("end_at")
    @classmethod
    def validate_time_order(cls, end_at: datetime, info):
        start_at = info.data.get("start_at")
        if start_at and not (start_at < end_at):
            raise ValueError("start_at must be < end_at")
        return end_at


class AppointmentRescheduleIn(BaseModel):
    """
    Body for PATCH /me/appointments/{id}/reschedule
    Client requests a reschedule.
    """
    start_at: datetime
    end_at: datetime

    @field_validator("end_at")
    @classmethod
    def validate_time_order(cls, end_at: datetime, info):
        start_at = info.data.get("start_at")
        if start_at and not (start_at < end_at):
            raise ValueError("start_at must be < end_at")
        return end_at


class AppointmentCancelIn(BaseModel):
    """
    Optional body for cancel endpoints.
    Client usually doesn't need a reason, but provider cancel might.
    """
    reason: str | None = Field(default=None, max_length=500)


class AppointmentOut(BaseModel):
    id: UUID
    client_id: UUID
    start_at: datetime
    end_at: datetime
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AppointmentCancelIn(BaseModel):
    reason: Optional[str] = None
