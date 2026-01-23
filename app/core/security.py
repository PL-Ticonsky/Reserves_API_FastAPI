"""

Purpose:
- Centralize security helpers: password hashing and JWT token handling.
- Ensure consistent auth behavior across the application.

What lives here:
1) Password hashing (bcrypt)
   - hash_password(): turns a plain password into a secure hash
   - verify_password(): checks a plain password against a stored hash

2) JWT tokens (access tokens)
   - create_access_token(): generates a signed token with user claims + expiration
   - decode_access_token(): validates and decodes token claims

Why this exists:
- Security should be implemented once, correctly, and reused everywhere.
- Routes/services should not re-implement crypto logic.

Usage examples:
    from app.core.security import hash_password, verify_password, create_access_token

    pwd_hash = hash_password("MyPass123!")
    assert verify_password("MyPass123!", pwd_hash) is True

    token = create_access_token(user_id="...", role="client")
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context (bcrypt)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password: Password provided by the user during registration.

    Returns:
        A bcrypt hash to store in the database (password_hash).

    Notes:
        - Never store plaintext passwords.
        - bcrypt includes a salt internally, so hashes differ even for same input.
    """
    if len(plain_password.encode("utf-8")) > 72:
        raise ValueError("Password is too long (bcrypt limit is 72 bytes).")

    if not plain_password or len(plain_password) < 8:
        # Basic guardrail (you can enforce stronger rules later)
        raise ValueError("Password must be at least 8 characters long.")
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password: Password provided at login.
        password_hash: Stored hash from DB.

    Returns:
        True if password matches, False otherwise.
    """
    if not plain_password or not password_hash:
        return False
    return _pwd_context.verify(plain_password, password_hash)


def create_access_token(*, user_id: str, role: str) -> str:
    """
    Create a signed JWT access token.

    Claims:
        - sub: subject (user_id)
        - role: user's role (client/provider)
        - iat: issued-at timestamp
        - exp: expiration timestamp

    Args:
        user_id: UUID string of the user.
        role: Role string ("client" or "provider").

    Returns:
        Encoded JWT token as a string.

    Notes:
        - Token is signed using settings.jwt_secret (HMAC-SHA256).
        - Expiration minutes are controlled by settings.jwt_expires_minutes.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expires_minutes)

    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: Raw JWT string (no "Bearer " prefix).

    Returns:
        Decoded payload (claims).

    Raises:
        jwt.ExpiredSignatureError: token expired
        jwt.InvalidTokenError: token invalid (signature, format, etc.)

    Notes:
        - This function only validates the token.
        - Authorization rules (role checks) are handled elsewhere (deps/services).
    """
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    return payload
