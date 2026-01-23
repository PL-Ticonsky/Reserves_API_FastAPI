"""
app/services/auth_service.py

Purpose:
- Implement authentication use-cases (register, login).
- Enforce business rules around auth (unique email, active users).
- Keep routers thin: routers only translate service errors -> HTTP responses.

Design:
- Repositories handle DB queries (data access).
- Services handle business rules and orchestration.
- Security helpers handle crypto (hashing/JWT).

This service raises domain-style errors (ValueError subclasses) so API layer
can convert them into consistent HTTP errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from app.repositories.user_repo import get_user_by_email, create_user


# ---------------------------
# Domain errors (service layer)
# ---------------------------

class EmailAlreadyExistsError(ValueError):
    """Raised when trying to register with an email that already exists."""


class InvalidCredentialsError(ValueError):
    """Raised when login credentials are invalid."""


class InactiveUserError(ValueError):
    """Raised when user exists but is inactive/disabled."""


# ---------------------------
# Return types
# ---------------------------

@dataclass(frozen=True)
class RegisterResult:
    id: str
    email: str
    role: str


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    token_type: str = "bearer"


# ---------------------------
# Use-cases
# ---------------------------

def register_client(db: Session, *, email: str, password: str) -> RegisterResult:
    """
    Register a new client user.

    Rules:
    - Email must be unique.
    - Password is stored as a hash (never plaintext).
    - New users default to role=client and is_active=true.

    Commits the transaction.
    """
    existing = get_user_by_email(db, email=email)
    if existing is not None:
        raise EmailAlreadyExistsError("EMAIL_ALREADY_EXISTS")

    pwd_hash = hash_password(password)

    user = User(
        email=email,
        password_hash=pwd_hash,
        role=UserRole.client,
    )

    create_user(db, user=user)
    db.commit()      # persist
    db.refresh(user) # load generated fields

    return RegisterResult(
        id=str(user.id),
        email=user.email,
        role=user.role.value,
    )


def login(db: Session, *, email: str, password: str) -> LoginResult:
    """
    Authenticate a user and return an access token.

    Rules:
    - Email must exist.
    - Password must match stored hash.
    - User must be active.

    Returns JWT token with:
    - sub = user.id
    - role = user.role
    """
    user = get_user_by_email(db, email=email)
    if user is None:
        # Don't reveal whether email exists
        raise InvalidCredentialsError("INVALID_CREDENTIALS")

    if not user.is_active:
        raise InactiveUserError("USER_INACTIVE")

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("INVALID_CREDENTIALS")

    token = create_access_token(user_id=str(user.id), role=user.role.value)

    return LoginResult(access_token=token)
