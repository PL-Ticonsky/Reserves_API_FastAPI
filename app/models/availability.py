"""
app/models/availability.py

Purpose:
- Defines weekly recurring availability blocks for the provider.
- Availability is defined by weekday and time range.
"""

import uuid
from sqlalchemy import Boolean, CheckConstraint, SmallInteger, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Availability(Base):
    __tablename__ = "provider_availability"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_availability_weekday_range"),
        CheckConstraint("start_time < end_time", name="ck_availability_time_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0..6
    start_time: Mapped[object] = mapped_column(Time, nullable=False)
    end_time: Mapped[object] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
