"""
app/db/session.py

Purpose:
- Create the SQLAlchemy database engine and session factory.
- Provide a `get_db()` dependency for FastAPI routes/services.

Responsibilities:
- Build the engine using DATABASE_URL from settings.
- Create SessionLocal for DB transactions.
- Yield a session and ensure it closes properly.

Usage:
    from app.db.session import get_db
    # In FastAPI: Depends(get_db)

Notes:
- This module does NOT create tables. Alembic migrations handle schema creation.
- If DATABASE_URL is wrong or the DB does not exist yet, connections will fail at runtime.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy Session.
    Ensures the session is closed after the request finishes.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
