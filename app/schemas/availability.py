"""
Purpose:
- Pydantic schemas for provider availability.
- Used by barber availability endpoints and slot generation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from datetime import time


class AvailabilityBlockIn(BaseModel):
    """
    Input block for POST /barber/availability/bulk
    """
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, end_time: time, info):
        start_time = info.data.get("start_time")
        if start_time and not (start_time < end_time):
            raise ValueError("start_time must be < end_time")
        return end_time


class AvailabilityBlockOut(BaseModel):
    """
    Output representation of an availability block.
    """
    id: str
    weekday: int
    start_time: time
    end_time: time
    is_active: bool
