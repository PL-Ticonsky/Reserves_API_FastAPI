"""
app/db/seed.py

Purpose:
- Seed initial data for the MVP (single provider user).
- Idempotent: running multiple times won't create duplicates.

What it seeds:
- A single provider user (barber) used to manage availability and appointments.

How to run:
- uv run python -m app.db.seed
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repo import get_user_by_email


def seed_provider(db: Session) -> User:
    """
    Ensure the MVP provider user exists.

    Rules:
    - If user with PROVIDER_EMAIL exists -> return it (no changes).
    - Otherwise create new provider with hashed password.

    Raises:
    - ValueError if PROVIDER_EMAIL / PROVIDER_PASSWORD not set.
    """
    email = getattr(settings, "provider_email", None)
    password = getattr(settings, "provider_password", None)

    if not email or not password:
        raise ValueError("Missing PROVIDER_EMAIL / PROVIDER_PASSWORD in .env")

    existing = get_user_by_email(db, email=email)
    if existing:
        return existing

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.provider,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    """
    CLI entrypoint.
    """
    db = SessionLocal()
    try:
        provider = seed_provider(db)
        print("seed ok:")
        print(f"  provider_id: {provider.id}")
        print(f"  email: {provider.email}")
        print(f"  role: {provider.role.value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
