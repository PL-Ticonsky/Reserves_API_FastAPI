"""
app/db/base.py

Purpose:
- Define the SQLAlchemy Declarative Base used by all ORM models.
- Import models so Alembic can discover metadata for migrations.

Usage:
    from app.db.base import Base
"""

from sqlalchemy.orm import DeclarativeBase
# Import models so Alembic can detect them
from app.models.user import User  # noqa: E402,F401
from app.models.availability import Availability  # noqa: E402,F401
from app.models.appointment import Appointment  # noqa: E402,F401

class Base(DeclarativeBase):
    pass



