"""
app/repositories/user_repo.py

Purpose:
- Data access for User entity.
- Keep DB queries out of routers/services.

Notes:
- This module only talks to the database.
- Business rules belong in services.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, *, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, *, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, *, user: User) -> User:
    db.add(user)
    db.flush()   # assigns PK without committing
    return user
