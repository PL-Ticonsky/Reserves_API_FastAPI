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


class Base(DeclarativeBase):
    pass

