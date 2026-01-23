
"""
app/api/deps.py

Purpose:
- Dependency functions for FastAPI routes (auth + DB access).
- Extract and validate JWT tokens from request headers.
- Load the current authenticated user from the database.
- Provide role-based guards (client/provider).

How it works:
- Client sends: Authorization: Bearer <token>
- We decode token -> get claims (sub=user_id, role)
- We fetch user from DB and return it as `current_user`.

These dependencies are used in routers to protect endpoints.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repo import get_user_by_id


# FastAPI helper that parses `Authorization: Bearer <token>`
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract JWT from Authorization header, validate it, and load the user.

    Returns:
        User (SQLAlchemy model) for the authenticated request.

    Raises:
        401 UNAUTHORIZED if token is missing/invalid/expired, or user not found/inactive.
    """
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    token = creds.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        # In production you might distinguish expired vs invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_TOKEN",
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_TOKEN",
        )

    # Validate UUID format
    try:
        user_id = UUID(str(sub))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_TOKEN",
        )

    user = get_user_by_id(db, user_id=user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    return user


def require_client(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure authenticated user has role=client.
    """
    if current_user.role != UserRole.client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN",
        )
    return current_user


def require_provider(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure authenticated user has role=provider.
    """
    if current_user.role != UserRole.provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN",
        )
    return current_user
